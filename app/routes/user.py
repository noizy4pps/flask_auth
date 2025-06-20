# app/routes/user.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('user', __name__)

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@bp.route('/settings')
@login_required
def user_settings():
    return render_template('user_settings.html', user=current_user)