# config.py
import os

class Config:
    # Global configuration
    APP_NAME = 'My App'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'devkey'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join('app/static', 'profile_pics')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Email configuration
    MAIL_SERVER = 'smtp.gmail.com' 
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'pippopluto5394@gmail.com'
    MAIL_PASSWORD = 'kfuu swoz dujz qogw'
    MAIL_DEFAULT_SENDER = 'pippopluto5394@gmail.com'
    
    # translations
    TRANSLATE = True
    LANGUAGES = {
    'en': 'English',
    'it': 'Italiano',
    'fr': 'Français'
    }
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'

    
    


