# app/routes/main.py
import os
import uuid
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from flask_login import login_required, current_user
from app import allowed_file
from config import Config


bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    print(session)
    return render_template('home.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@bp.route('/language')
def language():
    return render_template('language.html')



