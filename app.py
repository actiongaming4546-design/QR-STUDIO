from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo
import qrcode
from PIL import Image, ImageDraw
import io
import vobject
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import svgwrite
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import base64
from models import db, User, QRCode
from qrcode.image.svg import SvgImage
from datetime import datetime
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qr_studio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure uploads folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

logging.basicConfig(level=logging.INFO)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))
        new_user = User(email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'error')
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route("/dashboard")
@login_required
def dashboard():
    user_stats = {
        'total_qrcodes': current_user.qr_codes_created,
        'total_history': len(current_user.qr_history),
        'plan': current_user.plan.upper()
    }
    recent_qrs = QRCode.query.filter_by(user_id=current_user.id).order_by(QRCode.created_at.desc()).limit(10).all()
    return render_template("dashboard.html", stats=user_stats, recent_qrs=recent_qrs)

def geocode_location_safe(address, retries=3):
    """Safely geocode address with retry logic"""
    geolocator = Nominatim(user_agent="qr-studio-v1")
    for attempt in range(retries):
        try:
            location = geolocator.geocode(address, timeout=5)
            return location
        except GeocoderTimedOut:
            if attempt == retries - 1:
                return None
            continue
        except GeocoderServiceError:
            return None
    return None

def generate_qr_code(data, format_type='png', fg_color='#000000', bg_color='#FFFFFF', logo_file=None):
    """Generate QR code with given data and formatting options"""
    try:
        qr = qrcode.QRCode(
            version=1, 
            error_correction=qrcode.constants.ERROR_CORRECT_H, 
            box_size=10, 
            border=4
        )
        qr.add_data(data)
        qr.make(fit=True)

        if format_type == 'svg':
            img = qr.make_image(image_factory=SvgImage, fill_color=fg_color, back_color=bg_color)
            buf = io.BytesIO()
            img.save(buf)
            buf.seek(0)
            svg_data = buf.getvalue().decode('utf-8')
            return {
                'image': f"data:image/svg+xml;base64,{base64.b64encode(svg_data.encode()).decode()}",
                'mime': 'image/svg+xml'
            }
        else:
            img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert('RGB')

            if logo_file and format_type != 'svg':
                try:
                    logo_img = Image.open(logo_file).convert('RGBA')
                    logo_size = int(img.size[0] * 0.25)
                    logo_img = logo_img.resize((logo_size, logo_size))
                    pos_x = int((img.size[0] - logo_size) / 2)
                    pos_y = int((img.size[1] - logo_size) / 2)
                    img.paste(logo_img, (pos_x, pos_y), logo_img)
                except Exception as e:
                    logging.warning(f"Could not add logo: {e}")

            buf = io.BytesIO()
            if format_type == 'png':
                img.save(buf, format='PNG')
                mime = 'image/png'
            elif format_type == 'jpg':
                img.save(buf, format='JPEG')
                mime = 'image/jpeg'
            elif format_type == 'pdf':
                buf_pdf = io.BytesIO()
                c = canvas.Canvas(buf_pdf, pagesize=letter)
                c.drawImage(img, 100, 400, width=200, height=200)
                c.save()
                buf_pdf.seek(0)
                return {
                    'buffer': buf_pdf,
                    'mime': 'application/pdf',
                    'filename': 'qr.pdf'
                }
            else:
                img.save(buf, format='PNG')
                mime = 'image/png'

            buf.seek(0)
            image_data = base64.b64encode(buf.getvalue()).decode()
            return {
                'image': f"data:{mime};base64,{image_data}",
                'mime': mime
            }
    except Exception as e:
        logging.error(f"QR Generation error: {e}")
        return None

@app.route("/preview", methods=['POST'])
@login_required
def preview():
    """Preview QR code before downloading"""
    qr_type = request.form.get('type', '').strip()
    format_type = request.form.get('format', 'png').strip()
    fg_color = request.form.get('fg_color', '#000000').strip()
    bg_color = request.form.get('bg_color', '#FFFFFF').strip()
    logo = request.files.get('logo')

    # Validate inputs
    if not qr_type:
        return jsonify({'error': 'QR type is required'})

    data = ""
    
    try:
        if qr_type == 'url':
            data = request.form.get('url', '').strip()
            if not data.startswith(('http://', 'https://')):
                data = 'https://' + data
        elif qr_type == 'text':
            data = request.form.get('text', '').strip()
        elif qr_type == 'wifi':
            ssid = request.form.get('ssid', '').strip()
            password = request.form.get('password', '').strip()
            encryption = request.form.get('encryption', 'WPA').strip()
            if not ssid:
                return jsonify({'error': 'SSID is required'})
            data = f"WIFI:S:{ssid};T:{encryption};P:{password};;"
        elif qr_type == 'phone':
            phone = request.form.get('phone', '').strip()
            if not phone:
                return jsonify({'error': 'Phone number is required'})
            data = f"tel:{phone}"
        elif qr_type == 'sms':
            phone = request.form.get('phone', '').strip()
            if not phone:
                return jsonify({'error': 'Phone number is required'})
            data = f"sms:{phone}"
        elif qr_type == 'email':
            email = request.form.get('email', '').strip()
            if not email:
                return jsonify({'error': 'Email is required'})
            data = f"mailto:{email}"
        elif qr_type == 'contact':
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()
            if not (name or phone or email):
                return jsonify({'error': 'At least one contact field is required'})
            vcard = vobject.vCard()
            if name:
                vcard.add('fn').value = name
            if phone:
                vcard.add('tel').value = phone
            if email:
                vcard.add('email').value = email
            data = vcard.serialize()
        elif qr_type == 'location':
            address = request.form.get('address', '').strip()
            if not address:
                return jsonify({'error': 'Please enter a location address'})
            location = geocode_location_safe(address)
            if location:
                data = f"https://maps.google.com?q={location.latitude},{location.longitude}"
            else:
                return jsonify({'error': 'Location not found. Try a more specific address (city, street address, etc.)'})
        elif qr_type == 'event':
            title = request.form.get('event_title', '').strip()
            if not title:
                return jsonify({'error': 'Event title is required'})
            start_date = request.form.get('start_date', '').strip()
            location_ev = request.form.get('event_location', '').strip()
            data = f"BEGIN:VEVENT\nSUMMARY:{title}\nDTSTART:{start_date}\nLOCATION:{location_ev}\nEND:VEVENT"
        elif qr_type == 'wifi2':
            # Advanced WiFi QR with more options
            ssid = request.form.get('ssid', '').strip()
            password = request.form.get('password', '').strip()
            encryption = request.form.get('encryption', 'WPA').strip()
            hidden = request.form.get('hidden', 'false') == 'true'
            if not ssid:
                return jsonify({'error': 'SSID is required'})
            data = f"WIFI:S:{ssid};T:{encryption};P:{password};H:{'true' if hidden else 'false'};;"
        elif qr_type == 'payment':
            payment_id = request.form.get('payment_id', '').strip()
            if not payment_id:
                return jsonify({'error': 'Payment ID is required'})
            amount = request.form.get('payment_amount', '').strip()
            desc = request.form.get('payment_desc', '').strip()
            data = f"PAYMENT_ID:{payment_id}\nAMOUNT:{amount}\nDESC:{desc}"
        elif qr_type == 'order':
            order_number = request.form.get('order_number', '').strip()
            if not order_number:
                return jsonify({'error': 'Order number is required'})
            order_date = request.form.get('order_date', '').strip()
            order_details = request.form.get('order_details', '').strip()
            data = f"ORDER:{order_number}\nDATE:{order_date}\nDETAILS:{order_details}"
        elif qr_type == 'tracking':
            tracking_number = request.form.get('tracking_number', '').strip()
            if not tracking_number:
                return jsonify({'error': 'Tracking number is required'})
            carrier = request.form.get('carrier', '').strip()
            tracking_desc = request.form.get('tracking_desc', '').strip()
            data = f"TRACKING:{tracking_number}\nCARRIER:{carrier}\nDESC:{tracking_desc}"
        elif qr_type == 'invoice':
            invoice_number = request.form.get('invoice_number', '').strip()
            if not invoice_number:
                return jsonify({'error': 'Invoice number is required'})
            invoice_date = request.form.get('invoice_date', '').strip()
            invoice_amount = request.form.get('invoice_amount', '').strip()
            data = f"INVOICE:{invoice_number}\nDATE:{invoice_date}\nAMOUNT:{invoice_amount}"
        elif qr_type == 'product':
            product_code = request.form.get('product_code', '').strip()
            if not product_code:
                return jsonify({'error': 'Product code is required'})
            product_name = request.form.get('product_name', '').strip()
            product_details = request.form.get('product_details', '').strip()
            data = f"PRODUCT:{product_code}\nNAME:{product_name}\nDETAILS:{product_details}"
        elif qr_type == 'coupon':
            coupon_code = request.form.get('coupon_code', '').strip()
            if not coupon_code:
                return jsonify({'error': 'Coupon code is required'})
            coupon_discount = request.form.get('coupon_discount', '').strip()
            coupon_expiry = request.form.get('coupon_expiry', '').strip()
            data = f"COUPON:{coupon_code}\nDISCOUNT:{coupon_discount}\nEXPIRY:{coupon_expiry}"
        elif qr_type == 'appointment':
            appointment_datetime = request.form.get('appointment_datetime', '').strip()
            if not appointment_datetime:
                return jsonify({'error': 'Appointment date and time is required'})
            provider = request.form.get('appointment_provider', '').strip()
            service = request.form.get('appointment_service', '').strip()
            data = f"APPOINTMENT:{appointment_datetime}\nPROVIDER:{provider}\nSERVICE:{service}"
        else:
            return jsonify({'error': 'Unknown QR type'})

        if not data:
            return jsonify({'error': 'No data to encode'})

        result = generate_qr_code(data, format_type, fg_color, bg_color, logo)
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'Failed to generate QR code'})

    except Exception as e:
        logging.error(f"Preview error: {e}")
        return jsonify({'error': f'Error: {str(e)}'})

@app.route("/generate", methods=['POST'])
@login_required
def generate():
    """Generate and download QR code"""
    qr_type = request.form.get('type', '').strip()
    format_type = request.form.get('format', 'png').strip()
    title = request.form.get('title', f'QR-{datetime.now().strftime("%Y%m%d%H%M%S")}').strip()
    fg_color = request.form.get('fg_color', '#000000').strip()
    bg_color = request.form.get('bg_color', '#FFFFFF').strip()
    logo = request.files.get('logo')

    data = ""
    
    try:
        if qr_type == 'url':
            data = request.form.get('url', '').strip()
            if not data.startswith(('http://', 'https://')):
                data = 'https://' + data
        elif qr_type == 'text':
            data = request.form.get('text', '').strip()
        elif qr_type == 'wifi':
            ssid = request.form.get('ssid', '').strip()
            password = request.form.get('password', '').strip()
            encryption = request.form.get('encryption', 'WPA').strip()
            data = f"WIFI:S:{ssid};T:{encryption};P:{password};;"
        elif qr_type == 'phone':
            phone = request.form.get('phone', '').strip()
            data = f"tel:{phone}"
        elif qr_type == 'sms':
            phone = request.form.get('phone', '').strip()
            data = f"sms:{phone}"
        elif qr_type == 'email':
            email = request.form.get('email', '').strip()
            data = f"mailto:{email}"
        elif qr_type == 'contact':
            vcard = vobject.vCard()
            vcard.add('tel').value = request.form.get('phone', '')
            vcard.add('email').value = request.form.get('email', '')
            data = vcard.serialize()
        elif qr_type == 'location':
            address = request.form.get('address', '').strip()
            if not address:
                return jsonify({'error': 'Please enter a location address'})
            location = geocode_location_safe(address)
            if location:
                data = f"https://maps.google.com?q={location.latitude},{location.longitude}"
            else:
                return jsonify({'error': 'Location not found'})
        elif qr_type == 'payment':
            payment_id = request.form.get('payment_id', '').strip()
            if not payment_id:
                return jsonify({'error': 'Payment ID is required'})
            amount = request.form.get('payment_amount', '').strip()
            desc = request.form.get('payment_desc', '').strip()
            data = f"PAYMENT_ID:{payment_id}\nAMOUNT:{amount}\nDESC:{desc}"
        elif qr_type == 'order':
            order_number = request.form.get('order_number', '').strip()
            if not order_number:
                return jsonify({'error': 'Order number is required'})
            order_date = request.form.get('order_date', '').strip()
            order_details = request.form.get('order_details', '').strip()
            data = f"ORDER:{order_number}\nDATE:{order_date}\nDETAILS:{order_details}"
        elif qr_type == 'tracking':
            tracking_number = request.form.get('tracking_number', '').strip()
            if not tracking_number:
                return jsonify({'error': 'Tracking number is required'})
            carrier = request.form.get('carrier', '').strip()
            tracking_desc = request.form.get('tracking_desc', '').strip()
            data = f"TRACKING:{tracking_number}\nCARRIER:{carrier}\nDESC:{tracking_desc}"
        elif qr_type == 'invoice':
            invoice_number = request.form.get('invoice_number', '').strip()
            if not invoice_number:
                return jsonify({'error': 'Invoice number is required'})
            invoice_date = request.form.get('invoice_date', '').strip()
            invoice_amount = request.form.get('invoice_amount', '').strip()
            data = f"INVOICE:{invoice_number}\nDATE:{invoice_date}\nAMOUNT:{invoice_amount}"
        elif qr_type == 'product':
            product_code = request.form.get('product_code', '').strip()
            if not product_code:
                return jsonify({'error': 'Product code is required'})
            product_name = request.form.get('product_name', '').strip()
            product_details = request.form.get('product_details', '').strip()
            data = f"PRODUCT:{product_code}\nNAME:{product_name}\nDETAILS:{product_details}"
        elif qr_type == 'coupon':
            coupon_code = request.form.get('coupon_code', '').strip()
            if not coupon_code:
                return jsonify({'error': 'Coupon code is required'})
            coupon_discount = request.form.get('coupon_discount', '').strip()
            coupon_expiry = request.form.get('coupon_expiry', '').strip()
            data = f"COUPON:{coupon_code}\nDISCOUNT:{coupon_discount}\nEXPIRY:{coupon_expiry}"
        elif qr_type == 'appointment':
            appointment_datetime = request.form.get('appointment_datetime', '').strip()
            if not appointment_datetime:
                return jsonify({'error': 'Appointment date and time is required'})
            provider = request.form.get('appointment_provider', '').strip()
            service = request.form.get('appointment_service', '').strip()
            data = f"APPOINTMENT:{appointment_datetime}\nPROVIDER:{provider}\nSERVICE:{service}"

        if not data:
            return jsonify({'error': 'Invalid data'})

        result = generate_qr_code(data, format_type, fg_color, bg_color, logo)
        if result:
            # Save to database
            qr_record = QRCode(
                user_id=current_user.id,
                qr_type=qr_type,
                data=data,
                format_type=format_type,
                title=title,
                filename=f"{title}.{format_type}"
            )
            db.session.add(qr_record)
            current_user.qr_codes_created += 1
            db.session.commit()

            if 'buffer' in result:
                return send_file(
                    result['buffer'],
                    mimetype=result['mime'],
                    as_attachment=True,
                    download_name=f"{title}.{format_type}"
                )
            else:
                return jsonify(result)
        else:
            return jsonify({'error': 'Failed to generate QR code'})

    except Exception as e:
        logging.error(f"Generate error: {e}")
        return jsonify({'error': f'Error: {str(e)}'})

@app.route("/qr-history")
@login_required
def qr_history():
    """Get user's QR code history"""
    page = request.args.get('page', 1, type=int)
    qrs = QRCode.query.filter_by(user_id=current_user.id).order_by(QRCode.created_at.desc()).paginate(page=page, per_page=20)
    return jsonify({
        'qrs': [qr.to_dict() for qr in qrs.items],
        'total': qrs.total,
        'pages': qrs.pages
    })

@app.route("/qr-stats")
@login_required
def qr_stats():
    """Get user statistics"""
    total_qrs = current_user.qr_codes_created
    type_counts = db.session.query(QRCode.qr_type, db.func.count()).filter_by(user_id=current_user.id).group_by(QRCode.qr_type).all()
    format_counts = db.session.query(QRCode.format_type, db.func.count()).filter_by(user_id=current_user.id).group_by(QRCode.format_type).all()
    
    return jsonify({
        'total': total_qrs,
        'by_type': dict(type_counts),
        'by_format': dict(format_counts),
        'plan': current_user.plan
    })

@app.route("/delete-qr/<int:qr_id>", methods=['DELETE'])
@login_required
def delete_qr(qr_id):
    """Delete a QR code record"""
    qr = QRCode.query.filter_by(id=qr_id, user_id=current_user.id).first()
    if qr:
        db.session.delete(qr)
        current_user.qr_codes_created = max(0, current_user.qr_codes_created - 1)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'QR code not found'}), 404

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route("/features")
def features():
    return render_template("features.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/checkout-pro")
@login_required
def pro():
    return render_template("pricing.html")

@app.route("/checkout-business")
@login_required
def business():
    return render_template("pricing.html")

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)