# QR Generator - Deployment Guide

## 📦 Local Development Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/actiongaming4546-design/QR-STUDIO.git
   cd QR-STUDIO
   ```

2. **Create virtual environment**
   ```bash
   python -m venv qr-env
   source qr-env/bin/activate  # On Windows: qr-env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set:
   ```
   SECRET_KEY=your-super-secret-key-here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```
   
   Visit: `http://localhost:5000`

---

## 🚀 Deploy to Render

### Step 1: Create PostgreSQL Database on Render

1. Go to [Render.com](https://render.com)
2. Click "New +" → "PostgreSQL"
3. Fill in the form:
   - **Name**: qr-studio-db
   - **Database**: qr_studio_db
   - **User**: qr_studio_user
   - **Region**: Choose closest to you
4. Click "Create Database"
5. **Copy the Internal Database URL** (you'll need this)

### Step 2: Deploy Web Service

1. Go to [Render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Fill in the form:
   - **Name**: qr-generator (or your choice)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --workers 4 --bind 0.0.0.0:$PORT app:app`
   
5. **Click "Advanced" and add Environment Variables:**
   
   | Key | Value |
   |-----|-------|
   | `PYTHON_VERSION` | `3.11` |
   | `SECRET_KEY` | *Generate a secure key - use: `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `DATABASE_URL` | *Paste the Internal Database URL from Step 1* |
   | `FLASK_ENV` | `production` |

6. Click "Create Web Service"
7. Wait for deployment (3-5 minutes)

### Step 3: Initialize Database

Once deployed:

1. Go to your Render web service dashboard
2. Click "Shell" tab
3. Run:
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

4. Your app is now live! 🎉

---

## 🔧 Environment Variables

### Required for Render:
- `DATABASE_URL` - PostgreSQL connection string (auto-set by Render)
- `SECRET_KEY` - Secure secret key for Flask
- `FLASK_ENV` - Set to `production`

### Optional:
- `GEOLOCATION_API_KEY` - For advanced location services

---

## 📝 Available QR Code Types

1. **URL** - Link to websites
2. **WiFi** - WiFi connection info
3. **Phone** - Direct dial phone numbers
4. **SMS** - Send text messages
5. **Email** - Send emails
6. **Contact** - vCard contact info
7. **Location** - Google Maps coordinates
8. **Payment ID** - Payment tracking
9. **Order #** - Order numbers
10. **Tracking** - Package tracking
11. **Invoice** - Invoice numbers
12. **Product** - Product codes/SKU
13. **Coupon** - Discount codes
14. **Appointment** - Booking information

---

## 🐛 Troubleshooting

### Issue: "User data not saving"
**Solution**: Make sure `DATABASE_URL` environment variable is set in Render and the database was initialized using the Shell command.

### Issue: "Database error on login"
**Solution**: Run the database initialization command in Render Shell.

### Issue: "Port already in use"
**Solution**: This shouldn't happen on Render. If running locally, use `python app.py --port 8000`

### Issue: "Static files not loading"
**Solution**: Make sure `static/` folder exists with CSS and JS files.

---

## 📊 Application Stack

- **Backend**: Flask + Flask-SQLAlchemy
- **Database**: PostgreSQL (Render) / SQLite (Local)
- **Frontend**: HTML5 + CSS3 + JavaScript
- **QR Generation**: qrcode, Pillow
- **Authentication**: Flask-Login
- **Deployment**: Gunicorn on Render

---

## 📞 Support

For issues or questions:
- Check [Render Documentation](https://render.com/docs)
- Visit the [About Page](/about)
- Check [Features Page](/features)

---

**Status**: 🎨 BETA - Not yet released

Last updated: March 10, 2026
