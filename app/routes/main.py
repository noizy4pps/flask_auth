# app/routes/main.py
import os
import uuid
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from flask_login import login_required, current_user
from app import allowed_file
from app.models import UserDetails
from config import Config
from app import db


bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    print(session)
    print("is auth: ", current_user.is_authenticated)
    return render_template('home.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.details:
        details = UserDetails(user=current_user)
        db.session.add(details)
        db.session.commit()

    session['lang'] = current_user.details.pref_lang
    return render_template('dashboard.html')

@bp.route('/language')
def language():
    return render_template('language.html')



