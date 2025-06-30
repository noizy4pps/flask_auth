# app/routes/admin.py
from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from app import db
from app.forms import ChangeRoleForm, CreateEditorForm
from app.models import GlobalSettings, User
from app.routes.auth import send_confirmation_email
from app.utils.decorators import role_required
from werkzeug.security import generate_password_hash

bp = Blueprint('admin', __name__)

@bp.route('/create-editor', methods=['GET', 'POST'])
@login_required
@role_required('admin')  # Only allow admins
def create_editor():
    form = CreateEditorForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        if existing_user:
            flash('Username or email already exists.', 'error')
            return redirect(url_for('admin.create_editor'))  # or any page

        # Create and save new editor user
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='editor'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_confirmation_email(user)
        flash('Editor created successfully.')
        return redirect(url_for('main.dashboard'))  # or any page

    if request.method == 'POST':
        flash('Invalid form data.', 'error')
        return redirect(url_for('admin.create_editor'))  # or any page

    return render_template('create_editor.html', form=form)


# Admin-only global settings
@bp.route('/view-user-data', methods=['GET', 'POST'])
@login_required
@role_required('admin')  # Only allow admins
def view_user_data():
    userdata = User.query.all()
    """ if request.method == 'POST':
        for s in settings:
            s.setting_value = request.form.get(s.setting_name, '')
        db.session.commit()
        flash('Settings updated.') """
    return render_template('userdata.html', userdata=userdata)

# Admin-only global settings
@bp.route('/settings', methods=['GET', 'POST'])
@login_required
@role_required('admin')  # Only allow admins
def global_settings():
    settings = GlobalSettings.query.all()
    """ if request.method == 'POST':
        for s in settings:
            s.setting_value = request.form.get(s.setting_name, '')
        db.session.commit()
        flash('Settings updated.') """
    # reload_settings()
    return render_template('global_settings.html', settings=settings)
    
@bp.route('/settings/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')  # Only allow admins
def add_global_setting():
    if request.method == 'POST':
        name = request.form.get('setting_name')
        value = request.form.get('setting_value')
        desc = request.form.get('description')

        if GlobalSettings.query.filter_by(setting_name=name).first():
            flash('Setting already exists.')
            return redirect(url_for('admin.add_global_setting'))

        new_setting = GlobalSettings(setting_name=name, setting_value=value, description=desc)
        db.session.add(new_setting)
        db.session.commit()
        # Sync change with app.config
        current_app.config[new_setting.setting_name.upper()] = value
        # print(current_app.config[new_setting.setting_name.upper()])
        flash('Setting added.')
        return redirect(url_for('admin.global_settings'))

    return render_template('new_global_setting.html')

@bp.route('/settings/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')  # Only allow admins
def edit_global_setting(id):
    setting = GlobalSettings.query.get_or_404(id)

    if request.method == 'POST':
        setting.setting_name = request.form['setting_name']
        setting.setting_value = request.form['setting_value']
        setting.description = request.form['description']
        db.session.commit()
        # Sync change with app.config
        current_app.config[setting.setting_name.upper()] = request.form['setting_value']
        flash('Setting updated.')
        return redirect(url_for('admin.global_settings'))

    return render_template('edit_global_setting.html', setting=setting)

@bp.route('/settings/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')  # Only allow admins
def delete_global_setting(id):
    setting = GlobalSettings.query.get_or_404(id)
    db.session.delete(setting)
    db.session.commit()
    # Remove from config
    current_app.config.pop(setting.setting_name.upper(), None)
    flash('Setting deleted.')
    return redirect(url_for('admin.global_settings'))

@bp.route('/change-role', methods=['GET', 'POST'])
@login_required
@role_required('admin')  # Only allow admins
def change_role():
    form = ChangeRoleForm()
    # Populate dropdown with users
    form.user_id.choices = [(user.id, f"{user.username} ({user.email})  ({user.role})") for user in User.query.filter(User.id != current_user.id).all()]

    if form.validate_on_submit():
        user = User.query.get(form.user_id.data)
        if user:
            user.role = form.role.data
            db.session.commit()
            flash(f"{user.username}'s role has been changed to {user.role}")
            return redirect(url_for('admin.change_role'))
        else:
            flash('User not found')
    return render_template('change_role.html', form=form)

def reload_global_settings():
    settings = GlobalSettings.query.all()
    for s in settings:
        current_app.config[s.setting_name.upper()] = s.setting_value
        print(f"=={s.setting_name.upper()}={s.setting_value}==")
