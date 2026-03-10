#!/bin/bash
# Database initialization script for Render

echo "🔄 Initializing QR Generator Database..."

# Run the Flask initialization
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ Database tables created successfully!')
    print('📊 Tables created: User, QRCode')
    print('🚀 Application is ready to use!')
"

echo "✨ Database initialization complete!"
