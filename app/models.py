# app/models.py
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    profile_image = db.Column(db.String(200), default='default.png')
    is_confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    company = db.Column(db.String(100))
    last_pic = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', backref=db.backref('details', uselist=False, cascade='all, delete'))

# Global settings model
class GlobalSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting_name = db.Column(db.String(100), unique=True)
    setting_value = db.Column(db.String(200))
    description = db.Column(db.String(200))

    def get_typed_value(self):
        val = self.setting_value.strip()
        if val.isdigit():
            return int(val)
        try: return float(val)
        except ValueError:
            pass
        return val