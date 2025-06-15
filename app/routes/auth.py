# app/routes/auth.py
from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app import db, login_manager

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
            return jsonify({"message": "Logged in successfully."}), 200
        flash('Invalid username or password')
    return jsonify({"message": "Invalid data."}), 400

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out."}), 200

@bp.route('/register', methods=['POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered."}), 201
    return jsonify({"message": "Invalid registration data."}), 400