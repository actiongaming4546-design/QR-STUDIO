# QR Studio - QR Code Generator

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.3-green)
![Database](https://img.shields.io/badge/Database-PostgreSQL-darkblue)
![Status](https://img.shields.io/badge/Status-BETA-red)

A modern, professional QR code generator web application built with Flask. Generate QR codes for URLs, WiFi, contacts, payments, orders, and more!

## 🚀 Quick Start

### Local Development
```bash
git clone https://github.com/actiongaming4546-design/QR-STUDIO.git
cd QR-STUDIO
python -m venv qr-env
source qr-env/bin/activate  # Windows: qr-env\Scripts\activate
pip install -r requirements.txt
python app.py
```
Visit: `http://localhost:5000`

### Deploy to Render (Free Tier)
See [RENDER_DEPLOY.md](RENDER_DEPLOY.md) for detailed instructions.

**Quick Summary:**
1. Create PostgreSQL database on Render
2. Deploy web service from GitHub
3. Set environment variables (DATABASE_URL, SECRET_KEY, FLASK_ENV)
4. Done! Your app is live 🎉

---

## 📋 Features

### 14+ QR Code Types
- 🌐 **URL** - Link to websites
- 📶 **WiFi** - WiFi connection sharing
- 📞 **Phone** - Direct calling
- 💬 **SMS** - Text messages
- 📧 **Email** - Email composition
- 👥 **Contact** - vCard exchange
- 📍 **Location** - Google Maps links
- 💳 **Payment ID** - Payment tracking
- 🧾 **Order #** - Order numbers (food, retail, etc.)
- 📦 **Tracking** - Package tracking
- 📄 **Invoice** - Invoice management
- 📊 **Product** - Product codes/SKU
- 🎟️ **Coupon** - Discount codes
- 📅 **Appointment** - Booking information

### Advanced Features
✨ Custom colors (foreground & background)  
🖼️ Logo embedding  
📥 Multiple export formats (PNG, JPG, PDF, SVG)  
📊 QR code history and statistics  
🎨 Beautiful, responsive UI  
⚡ Fast generation  
🔒 Secure data handling  

---

## 🛠️ Tech Stack

- **Backend**: Flask 3.1.3, Flask-Login, Flask-SQLAlchemy
- **Database**: PostgreSQL (production) / SQLite (local)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **QR Generation**: qrcode, Pillow, ReportLab
- **Location Services**: geopy
- **Server**: Gunicorn
- **Deployment**: Render.com

---

## 📁 Project Structure

```
QR-STUDIO/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment config
├── render.yaml           # Alternative config
├── .env.example          # Environment template
├── RENDER_DEPLOY.md      # Deployment guide
├── templates/            # HTML pages
│   ├── index.html
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── pricing.html
│   ├── features.html
│   ├── about.html
│   ├── 404.html
│   └── 500.html
├── static/               # Assets
│   ├── style.css
│   └── script.js
└── uploads/              # User uploads
```

---

## 🔐 Environment Variables

### Production (Render)
```env
FLASK_ENV=production
SECRET_KEY=your-secure-random-key
DATABASE_URL=postgresql://user:pass@host:port/db
```

### Local Development
```env
FLASK_ENV=development
SECRET_KEY=dev-key
# DATABASE_URL is optional (uses SQLite by default)
```

---

## 📖 Usage

### Generate a Simple QR Code

1. **Register** - Create an account
2. **Login** - Access the dashboard
3. **Select QR Type** - Choose from 14+ options
4. **Fill Details** - Enter the data
5. **Download** - Get your QR code in PNG, JPG, SVG, or PDF

### Advanced Options
- Add your logo to the QR code
- Customize colors
- Preview before download
- View your QR code history
- Download statistics

---

## 🚢 Deployment

### Render.com (Recommended for Free Tier)
Supports both Procfile and render.yaml configurations.

**Environment Setup Required:**
- PostgreSQL database
- Flask environment variables
- Gunicorn web server

See [RENDER_DEPLOY.md](RENDER_DEPLOY.md) for complete instructions.

### Other Platforms
- Heroku (deprecated free tier)
- AWS, Azure, Google Cloud
- Self-hosted on VPS

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Pages not loading | Ensure `static/` and `templates/` dirs are tracked in git |
| Database errors | Check `DATABASE_URL` is set correctly (use Internal URL on Render) |
| Dashboard not loading | Verify the database is initialized and reachable |
| Static files missing | Run `git add -A && git commit` to track files |
| Blank pages | Check Render logs for Flask errors |

---

## 📝 Available Routes

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/` | GET | No | Homepage |
| `/dashboard` | GET | No | QR creation dashboard |
| `/preview` | POST | No | Preview QR code |
| `/generate` | POST | No | Generate & download QR |
| `/pricing` | GET | No | Pricing page |
| `/features` | GET | No | Features page |
| `/about` | GET | No | About page |
| `/qr-history` | GET | No | QR history |
| `/qr-stats` | GET | No | Usage statistics |
| `/delete-qr/<id>` | DELETE | No | Delete QR code |

---

## 🤝 Contributing

Pull requests are welcome! For major changes:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 📞 Support

- 📖 [Deployment Guide](RENDER_DEPLOY.md)
- 🐛 [GitHub Issues](https://github.com/actiongaming4546-design/QR-STUDIO/issues)
- 💬 [Features Page](/features)
- ℹ️ [About Page](/about)

---

## ✨ Status

🎨 **BETA** - Not yet released to the public

This application is under active development. All features are working but may change before the official release.

---

**Made with ❤️ by [Anudeep Singh](https://github.com/actiongaming4546-design)**

**Last Updated:** March 10, 2026

**Repository:** [GitHub - QR-STUDIO](https://github.com/actiongaming4546-design/QR-STUDIO)
