# app/routes/user.py

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import login_required, current_user
from app import db
from app.forms import UserDetailsForm
from app.models import UserDetails

bp = Blueprint('user', __name__)

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@bp.route('/settings')
@login_required
def user_settings():
    return render_template('user_settings.html', user=current_user)

@bp.route('/details', methods=['GET', 'POST'])
@login_required
def edit_details():
    details = current_user.details or UserDetails(user=current_user)
    form = UserDetailsForm(obj=details)
    if form.validate_on_submit():
        form.populate_obj(details)
        db.session.add(details)
        db.session.commit()
        flash('Details updated.')
        return redirect(url_for('user.profile'))
    return render_template('edit_details.html', form=form)

@bp.route('/set_language', methods=['POST'])
def set_language():
    session['lang'] = request.form['lang']
    return redirect(request.referrer or url_for('main.home'))