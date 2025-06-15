# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.dashboard'))  # or any page you like
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out."}), 200

@bp.route('/register', methods=['POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
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