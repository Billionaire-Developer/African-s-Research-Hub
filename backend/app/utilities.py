from functools import wraps
from flask import jsonify
from flask_login import current_user
from email_validator import validate_email, EmailNotValidError

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        if current_user.role.lower() != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        if current_user.role.lower() != "student":
            return jsonify({"error": "Student access required"}), 403
        return f(*args, **kwargs)
    return decorated_function


def is_valid_email(email):
    try:
        valid = validate_email(email)
        return valid.email
    except EmailNotValidError:
        return None