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
    MAIL_SERVER = 'smtp.gmail.com'   # or your SMTP server
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'youremail@example.com'
    MAIL_PASSWORD = 'your mail provider app pw'
    MAIL_DEFAULT_SENDER = 'youremail@example.com'
    
    # translations
    TRANSLATE = True
    LANGUAGES = {
    'en': 'English',
    'it': 'Italiano',
    'fr': 'Français',
    'es': 'Español',
    'de': 'Deutsch',
    'pt': 'Português',
    'zh_CN': '简体中文'
}
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'

    
    


