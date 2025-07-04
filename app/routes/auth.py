# app/routes/auth.py
from datetime import datetime
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app.models import GlobalSettings, User
from app.forms import LoginForm, RegistrationForm, RequestResetForm, ResetPasswordForm, UpdateEmailForm, UpdatePasswordForm
from app import allowed_file, db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import Email
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_mail import Message
from app import mail  # ensure mail = Mail(app) is in your app factory
from sqlalchemy.exc import SQLAlchemyError
from config import Config

bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm-salt')

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-confirm-salt',
            max_age=expiration
        )
    except Exception:
        return False
    return email

def send_confirmation_email(user):
    try:
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        html = f'<p>Hi {user.username}, click the link to confirm your email:</p><a href="{confirm_url}">Confirm Email</a>'
        msg = Message('Confirm Your Email', recipients=[user.email], html=html)
        mail.send(msg)
    except Exception as e:
        flash(f"Error sending confirmation email: {e}")


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.dashboard'))  # or any page
        flash('Invalid username or password')
    if request.method == 'POST':
        flash('Invalid data.', 'error')
        return redirect(url_for('auth.login'))  # or any page
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_confirmation_email(user)
        flash('User registered. A confirmation email has been sent.', 'success')
        return redirect(url_for('auth.login'))  # or any page
    if request.method == 'POST':
        flash('Invalid registration data.', 'error')
        return redirect(url_for('auth.register'))  # or any page
    return render_template('register.html', form=form)

@bp.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.is_confirmed:
        flash('Account already confirmed. Please login.', 'info')
    else:
        user.is_confirmed = True
        user.confirmed_on = datetime.utcnow()
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/app-setup', methods=['GET'])
def app_setup():
    settings_to_create = {
        'TRACK_USERS_EMAIL_CHANGE': 'false',
        'TRACK_USERS_SIGNUP': 'false'
    }

    created_settings = []

    try:
        for key, val in settings_to_create.items():
            existing = GlobalSettings.query.filter_by(setting_name=key).first()
            if not existing:
                setting = GlobalSettings(
                    setting_name=key,
                    setting_value=val,
                    description=f'System setting: {key.replace("_", " ").title()}'
                )
                db.session.add(setting)
                created_settings.append(setting)

        if created_settings:
            db.session.commit()
            return render_template('setup_success.html')  # shows the "Create Admin" button
        else:
            return jsonify({'error': 'Settings already exist. Setup not required.'}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Error creating global settings', 'details': str(e)}), 500

@bp.route('/create-admin', methods=['GET'])
def create_admin():
    username = "admin123"
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "admin already exists."}), 400

    password = "admin123"
    hashed = generate_password_hash(password)
    email = "youremail@gmail.com"
    user_is_confirmed = True
    user_confirmed_on = datetime.utcnow()
    admin = User(username=username, email=email, password_hash=hashed, role='admin', is_confirmed=user_is_confirmed, confirmed_on=user_confirmed_on)
    db.session.add(admin)
    db.session.commit()
    return jsonify({"message": "admin registered successfully."}), 201

# Upload profile image
@bp.route('/upload_profile', methods=['GET', 'POST'])
@login_required
def upload_profile():
    if request.method == 'POST':
        file = request.files.get('profile_pic')
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"user{current_user.id}_{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

            # Delete old image if not default
            if current_user.profile_image != 'default.png':
                try:
                    os.remove(os.path.join(Config.UPLOAD_FOLDER, current_user.profile_image))
                except FileNotFoundError:
                    pass

            file.save(filepath)
            current_user.profile_image = filename
            db.session.commit()
            flash('Profile image updated.')
            return redirect(url_for('main.dashboard'))

        flash('Invalid file.')
    return render_template('upload_profile.html')

@bp.route('/update-email', methods=['GET', 'POST'])
@login_required
def update_email():
    form = UpdateEmailForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        db.session.commit()
        flash("Email updated.")
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        flash("Invalid email data.")
        return render_template('update_email.html', form=form)
    return render_template('update_email.html', form=form)

@bp.route('/update-password', methods=['GET', 'POST'])
@login_required
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            return jsonify({"message": "Current password is incorrect."}), 400
        current_user.set_password(form.password.data)
        db.session.commit()
        flash("Password updated.")
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        flash("Invalid password data.")
        return render_template('update_password.html', form=form)
    return render_template('update_password.html', form=form)

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_confirmation_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            msg = Message('Password Reset Request', recipients=[user.email])
            msg.body = f'Reset your password using the following link (valid for 1 hour): {reset_url}'
            mail.send(msg)
        flash("If your email is registered, you will receive a password reset link.")
        return redirect(url_for('main.dashboard'))
    return render_template('forgot_password.html', form=form)

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_token(token)
    if not email:
        return jsonify({"message": "The reset link is invalid or has expired."}), 400
    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Password has been reset.")
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)

@bp.route('/resend_confirmation', methods=['POST'])
@login_required
def resend_confirmation():
    if current_user.is_confirmed:
        flash('Your account is already confirmed.')
    else:
        try:
            send_confirmation_email(current_user)
            flash('Confirmation email resent.')
        except Exception as e:
            flash('Error sending confirmation email.')
    return redirect(url_for('user.profile'))




