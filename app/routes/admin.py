# app/routes/admin.py
from flask import Blueprint, jsonify
from flask_login import login_required, current_user

bp = Blueprint('admin', __name__)

@bp.route('/create-editor', methods=['POST'])
@login_required
def create_editor():
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    # logic to create editor (stub)
    return jsonify({"message": "Editor created."}), 201