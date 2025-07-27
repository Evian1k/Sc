from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, School, Student, Staff
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/system-info', methods=['GET'])
@jwt_required()
def get_system_info():
    """Get system information (superadmin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role != 'superadmin':
            return jsonify({'error': 'Unauthorized'}), 403

        total_schools = School.query.count()
        total_users = User.query.count()
        total_students = Student.query.count()
        total_staff = Staff.query.count()

        return jsonify({
            'system_info': {
                'total_schools': total_schools,
                'total_users': total_users,
                'total_students': total_students,
                'total_staff': total_staff,
                'version': '1.0.0',
                'last_updated': datetime.utcnow().isoformat()
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role not in ['admin', 'superadmin']:
            return jsonify({'error': 'Unauthorized'}), 403

        if user.role == 'admin':
            # School admin sees only their school's users
            users = User.query.filter_by(school_id=user.school_id).all()
        else:
            # Superadmin sees all users
            users = User.query.all()

        return jsonify({
            'users': [u.to_dict() for u in users],
            'total': len(users)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@jwt_required()
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user or current_user.role not in ['admin', 'superadmin']:
            return jsonify({'error': 'Unauthorized'}), 403

        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404

        # Check permissions
        if current_user.role == 'admin' and target_user.school_id != current_user.school_id:
            return jsonify({'error': 'Unauthorized'}), 403

        target_user.is_active = not target_user.is_active
        db.session.commit()

        return jsonify({
            'message': f'User {"activated" if target_user.is_active else "deactivated"} successfully',
            'user': target_user.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500