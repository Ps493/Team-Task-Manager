"""
middleware/auth.py - JWT decorators + role-based access control
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import User


def get_current_user():
    """Return the currently authenticated User object."""
    user_id = get_jwt_identity()
    print(f"DEBUG identity: {user_id!r}, type: {type(user_id)}")
    return User.query.get(int(user_id))


def jwt_required_custom(fn):
    """Decorator: require a valid JWT token."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            return jsonify({"error": "Authorization token required"}), 401
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    """Decorator: require a valid JWT token AND admin role."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({"error": "Authorization token required"}), 401

        user = get_current_user()
        
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403

        return fn(*args, **kwargs)
    return wrapper
