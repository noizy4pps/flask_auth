# app/routes/main.py
from flask import Blueprint, jsonify
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return jsonify({"message": "Welcome to the home page."})

@bp.route('/dashboard')
@login_required
def dashboard():
    return jsonify({"message": f"Welcome {current_user.username} to your dashboard."})

