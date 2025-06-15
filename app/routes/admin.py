# app/routes/admin.py
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from app import db
from app.models import GlobalSettings

bp = Blueprint('admin', __name__)

@bp.route('/create-editor', methods=['POST'])
@login_required
def create_editor():
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    # logic to create editor (stub)
    return jsonify({"message": "Editor created."}), 201

# Admin-only global settings
@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('main.dashboard'))

    settings = GlobalSettings.query.all()
    """ if request.method == 'POST':
        for s in settings:
            s.setting_value = request.form.get(s.setting_name, '')
        db.session.commit()
        flash('Settings updated.') """
    return render_template('settings.html', settings=settings)
    
@bp.route('/settings/new', methods=['GET', 'POST'])
@login_required
def add_setting():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('setting_name')
        value = request.form.get('setting_value')
        desc = request.form.get('description')

        if GlobalSettings.query.filter_by(setting_name=name).first():
            flash('Setting already exists.')
            return redirect(url_for('admin.add_setting'))

        new_setting = GlobalSettings(setting_name=name, setting_value=value, description=desc)
        db.session.add(new_setting)
        db.session.commit()
        flash('Setting added.')
        return redirect(url_for('admin.settings'))

    return render_template('new_setting.html')

@bp.route('/settings/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_setting(id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('main.dashboard'))

    setting = GlobalSettings.query.get_or_404(id)

    if request.method == 'POST':
        setting.setting_name = request.form['setting_name']
        setting.setting_value = request.form['setting_value']
        setting.description = request.form['description']
        db.session.commit()
        flash('Setting updated.')
        return redirect(url_for('admin.settings'))

    return render_template('edit_setting.html', setting=setting)

@bp.route('/settings/delete/<int:id>', methods=['POST'])
@login_required
def delete_setting(id):
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('main.dashboard'))

    setting = GlobalSettings.query.get_or_404(id)
    db.session.delete(setting)
    db.session.commit()
    flash('Setting deleted.')
    return redirect(url_for('admin.settings'))