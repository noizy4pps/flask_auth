# app/__init__.py
import os
from flask import Flask, request, g, session
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from flask_babel import Babel, _,lazy_gettext as _l, gettext
from flask_wtf import CSRFProtect

# Extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

login_manager.login_view = 'auth.login'
mail = Mail()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # load GlobalSettings model values
    from app.models import GlobalSettings
    with app.app_context():
        db.create_all()
        settings = GlobalSettings.query.all()
        for setting in settings:
            app.config[setting.setting_name.upper()] = setting.setting_value

    from app.routes import main, auth, admin, user
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(user, url_prefix='/user')

    mail.init_app(app)

    # datetime filter format
    from app.filters import format_date, relative_time
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['relative'] = relative_time

    # translations setup
    def get_locale():
        # Check if the language query parameter is set and valid
        if 'lang' in request.args:
            lang = request.args.get('lang')
            if lang in ['en', 'fr']:
                session['lang'] = lang
                return session['lang']
        # If not set via query, check if we have it stored in the session
        elif 'lang' in session:
            return session.get('lang')
        # Otherwise, use the browser's preferred language
        return request.accept_languages.best_match(app.config['LANGUAGES'])

    babel = Babel(app, locale_selector=get_locale)

    if not app.config.get('TRANSLATE', False):
        babel.init_app(app)

    csrf.init_app(app) 

    return app

__all__ = ['mail']

# Utility: check allowed file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

