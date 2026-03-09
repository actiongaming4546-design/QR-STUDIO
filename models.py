from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    qr_codes_created = db.Column(db.Integer, default=0)
    plan = db.Column(db.String(20), default='free')  # free, pro, premium
    
    qr_history = db.relationship('QRCode', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    qr_type = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Text, nullable=False)
    format_type = db.Column(db.String(20), default='png')
    filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    downloads = db.Column(db.Integer, default=0)
    title = db.Column(db.String(200))
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.qr_type,
            'title': self.title,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'downloads': self.downloads,
            'format': self.format_type
        }