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
import svgwrite
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import base64
from models import db, User
from qrcode.image.svg import SvgImage

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qr_studio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
            flash('Email already registered.')
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
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.')
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/preview", methods=['POST'])
@login_required
def preview():
    qr_type = request.form.get('type')
    format_type = request.form.get('format', 'png')
    # colors fixed to black on white
    fg_color = '#000000'
    bg_color = '#FFFFFF'
    logo = request.files.get('logo')

    data = ""
    if qr_type == 'url':
        data = request.form.get('url')
    elif qr_type == 'wifi':
        ssid = request.form.get('ssid')
        password = request.form.get('password')
        encryption = request.form.get('encryption', 'WPA')
        data = f"WIFI:S:{ssid};T:{encryption};P:{password};;"
    elif qr_type == 'phone':
        data = f"tel:{request.form.get('phone')}"
    elif qr_type == 'sms':
        data = f"sms:{request.form.get('phone')}"
    elif qr_type == 'email':
        data = f"mailto:{request.form.get('email')}"
    elif qr_type == 'contact':
        vcard = vobject.vCard()
        
        vcard.add('tel').value = request.form.get('phone')
        vcard.add('email').value = request.form.get('email')
        data = vcard.serialize()
    elif qr_type == 'location':
        address = request.form.get('address')
        geolocator = Nominatim(user_agent="qr-studio")
        location = geolocator.geocode(address)
        if location:
            data = f"https://www.google.com/maps?q={location.latitude},{location.longitude}"
        else:
            data = "Location not found"

    if not data:
        return jsonify({'error': 'Invalid data'})

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    if format_type == 'svg':
        img = qr.make_image(image_factory=SvgImage, fill_color=fg_color, back_color=bg_color)
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)
        svg_data = buf.getvalue().decode('utf-8')
        return jsonify({'image': f"data:image/svg+xml;base64,{base64.b64encode(svg_data.encode()).decode()}"})
    else:
        img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert('RGB')

    if logo and format_type != 'svg':
        logo_img = Image.open(logo).convert('RGBA')
        logo_img = logo_img.resize((50, 50))
        img.paste(logo_img, (img.size[0]//2 - 25, img.size[1]//2 - 25), logo_img)

    buf = io.BytesIO()
    if format_type == 'png':
        img.save(buf, format='PNG')
        mime = 'image/png'
    elif format_type == 'jpg':
        img.save(buf, format='JPEG')
        mime = 'image/jpeg'
    elif format_type == 'pdf':
        c = canvas.Canvas(buf, pagesize=letter)
        c.drawImage(img, 100, 400, width=200, height=200)
        c.save()
        mime = 'application/pdf'
    buf.seek(0)
    image_data = base64.b64encode(buf.getvalue()).decode()
    return jsonify({'image': f"data:{mime};base64,{image_data}"})

@app.route("/generate", methods=['POST'])
@login_required
def generate():
    # Same as preview but for download
    qr_type = request.form.get('type')
    format_type = request.form.get('format', 'png')
    fg_color = '#000000'
    bg_color = '#FFFFFF'
    logo = request.files.get('logo')

    data = ""
    if qr_type == 'url':
        data = request.form.get('url')
    elif qr_type == 'wifi':
        ssid = request.form.get('ssid')
        password = request.form.get('password')
        encryption = request.form.get('encryption', 'WPA')
        data = f"WIFI:S:{ssid};T:{encryption};P:{password};;"
    elif qr_type == 'phone':
        data = f"tel:{request.form.get('phone')}"
    elif qr_type == 'sms':
        data = f"sms:{request.form.get('phone')}"
    elif qr_type == 'email':
        data = f"mailto:{request.form.get('email')}"
    elif qr_type == 'contact':
        vcard = vobject.vCard()
        
        vcard.add('tel').value = request.form.get('phone')
        vcard.add('email').value = request.form.get('email')
        data = vcard.serialize()
    elif qr_type == 'location':
        address = request.form.get('address')
        geolocator = Nominatim(user_agent="qr-studio")
        location = geolocator.geocode(address)
        if location:
            data = f"https://www.google.com/maps?q={location.latitude},{location.longitude}"
        else:
            data = "Location not found"

    if not data:
        return jsonify({'error': 'Invalid data'})

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    if format_type == 'svg':
        img = qr.make_image(image_factory=SvgImage, fill_color=fg_color, back_color=bg_color)
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)
        return send_file(buf, mimetype='image/svg+xml', as_attachment=True, download_name='qr.svg')
    else:
        img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert('RGB')

    if logo and format_type != 'svg':
        logo_img = Image.open(logo).convert('RGBA')
        logo_img = logo_img.resize((50, 50))
        img.paste(logo_img, (img.size[0]//2 - 25, img.size[1]//2 - 25), logo_img)

    if format_type == 'png':
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png', as_attachment=True, download_name='qr.png')
    elif format_type == 'jpg':
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)
        return send_file(buf, mimetype='image/jpeg', as_attachment=True, download_name='qr.jpg')
    elif format_type == 'pdf':
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.drawImage(img, 100, 400, width=200, height=200)
        c.save()
        buf.seek(0)
        return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name='qr.pdf')

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route("/checkout-pro")
@login_required
def pro():
    return "<h1>Pro plan coming soon</h1>"

@app.route("/checkout-business")
@login_required
def business():
    return "<h1>Business plan coming soon</h1>"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)