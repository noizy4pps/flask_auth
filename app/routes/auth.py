# app/routes/auth.py
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app import allowed_file, db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import Email

from config import Config

bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        flash('User registered.', 'success')
        return redirect(url_for('auth.login'))  # or any page
    if request.method == 'POST':
        flash('Invalid registration data.', 'error')
        return redirect(url_for('auth.register'))  # or any page
    return render_template('register.html', form=form)

@bp.route('/create-admin', methods=['GET'])
def create_admin():
    username = "admin123"
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "admin already exists."}), 400

    password = "admin123"
    hashed = generate_password_hash(password)
    email = "email@example.com"
    admin = User(username=username, email=email, password_hash=hashed, role='admin')
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