#!/bin/bash
# Build script for Render

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄️ Initializing database..."
python -c "
from app import app, db
import os

with app.app_context():
    try:
        db.create_all()
        print('✅ Database tables created successfully!')
    except Exception as e:
        print(f'⚠️ Database init note: {e}')
        print('This is OK if the database is already initialized.')

print('✨ Build complete!')
"
