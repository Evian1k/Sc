from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Timetable
from datetime import datetime

timetables_bp = Blueprint('timetables', __name__)

@timetables_bp.route('', methods=['GET'])
@jwt_required()
def get_timetables():
    """Get timetables for the school"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        timetables = Timetable.query.filter_by(school_id=user.school_id).all()

        return jsonify({
            'timetables': [timetable.to_dict() for timetable in timetables],
            'total': len(timetables)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@timetables_bp.route('', methods=['POST'])
@jwt_required()
def create_timetable():
    """Create a new timetable entry"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()

        timetable = Timetable(
            school_id=user.school_id,
            class_id=data.get('class_id'),
            subject_id=data.get('subject_id'),
            teacher_id=data.get('teacher_id'),
            day_of_week=data.get('day_of_week'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            room_number=data.get('room_number'),
            academic_year=data.get('academic_year'),
            term=data.get('term'),
            created_by_id=user.id
        )

        db.session.add(timetable)
        db.session.commit()

        return jsonify({
            'message': 'Timetable entry created successfully',
            'timetable': timetable.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500