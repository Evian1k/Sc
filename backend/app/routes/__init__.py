from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User


def current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id) if user_id else None


def require_role(*allowed_roles):
    def decorator(fn):
        from functools import wraps

        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user or user.role not in allowed_roles:
                return jsonify({'error': 'Forbidden'}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def enforce_school_scope(query, user):
    if not user:
        return query.filter(False)
    if user.role == 'platform_owner':
        return query
    return query.filter_by(school_id=user.school_id)