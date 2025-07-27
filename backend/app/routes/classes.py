from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Class, Subject, User, Staff
from datetime import datetime

classes_bp = Blueprint('classes', __name__)

@classes_bp.route('', methods=['GET'])
@jwt_required()
def get_classes():
    """Get all classes for the school"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        classes = Class.query.filter_by(school_id=user.school_id).all()

        return jsonify({
            'classes': [cls.to_dict() for cls in classes],
            'total': len(classes)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@classes_bp.route('', methods=['POST'])
@jwt_required()
def create_class():
    """Create a new class"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'academic_year', 'term']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        class_obj = Class(
            school_id=user.school_id,
            name=data['name'],
            description=data.get('description'),
            academic_year=data['academic_year'],
            term=data['term'],
            class_teacher_id=data.get('class_teacher_id'),
            capacity=data.get('capacity'),
            room_number=data.get('room_number'),
            created_by_id=user.id
        )

        db.session.add(class_obj)
        db.session.commit()

        return jsonify({
            'message': 'Class created successfully',
            'class': class_obj.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@classes_bp.route('/<int:class_id>', methods=['GET'])
@jwt_required()
def get_class(class_id):
    """Get specific class details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        class_obj = Class.query.get(class_id)
        if not class_obj or class_obj.school_id != user.school_id:
            return jsonify({'error': 'Class not found'}), 404

        return jsonify({'class': class_obj.to_dict()})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@classes_bp.route('/<int:class_id>', methods=['PUT'])
@jwt_required()
def update_class(class_id):
    """Update class information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        class_obj = Class.query.get(class_id)
        if not class_obj or class_obj.school_id != user.school_id:
            return jsonify({'error': 'Class not found'}), 404

        data = request.get_json()

        # Update fields
        updatable_fields = ['name', 'description', 'academic_year', 'term', 
                           'class_teacher_id', 'capacity', 'room_number']

        for field in updatable_fields:
            if field in data:
                setattr(class_obj, field, data[field])

        class_obj.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Class updated successfully',
            'class': class_obj.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@classes_bp.route('/<int:class_id>', methods=['DELETE'])
@jwt_required()
def delete_class(class_id):
    """Delete a class"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        class_obj = Class.query.get(class_id)
        if not class_obj or class_obj.school_id != user.school_id:
            return jsonify({'error': 'Class not found'}), 404

        # Check if class has students
        if class_obj.students:
            return jsonify({'error': 'Cannot delete class with enrolled students'}), 400

        db.session.delete(class_obj)
        db.session.commit()

        return jsonify({'message': 'Class deleted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Subject routes
@classes_bp.route('/subjects', methods=['GET'])
@jwt_required()
def get_subjects():
    """Get all subjects for the school"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        subjects = Subject.query.filter_by(school_id=user.school_id).all()

        return jsonify({
            'subjects': [subject.to_dict() for subject in subjects],
            'total': len(subjects)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@classes_bp.route('/subjects', methods=['POST'])
@jwt_required()
def create_subject():
    """Create a new subject"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Check if subject code already exists
        existing_subject = Subject.query.filter_by(
            school_id=user.school_id,
            code=data['code']
        ).first()

        if existing_subject:
            return jsonify({'error': 'Subject code already exists'}), 409

        subject = Subject(
            school_id=user.school_id,
            name=data['name'],
            code=data['code'],
            description=data.get('description'),
            teacher_id=data.get('teacher_id'),
            class_id=data.get('class_id'),
            credit_hours=data.get('credit_hours'),
            is_mandatory=data.get('is_mandatory', True),
            created_by_id=user.id
        )

        db.session.add(subject)
        db.session.commit()

        return jsonify({
            'message': 'Subject created successfully',
            'subject': subject.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@classes_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@jwt_required()
def update_subject(subject_id):
    """Update subject information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        subject = Subject.query.get(subject_id)
        if not subject or subject.school_id != user.school_id:
            return jsonify({'error': 'Subject not found'}), 404

        data = request.get_json()

        # Update fields
        updatable_fields = ['name', 'code', 'description', 'teacher_id', 
                           'class_id', 'credit_hours', 'is_mandatory']

        for field in updatable_fields:
            if field in data:
                setattr(subject, field, data[field])

        subject.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Subject updated successfully',
            'subject': subject.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@classes_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@jwt_required()
def delete_subject(subject_id):
    """Delete a subject"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        subject = Subject.query.get(subject_id)
        if not subject or subject.school_id != user.school_id:
            return jsonify({'error': 'Subject not found'}), 404

        db.session.delete(subject)
        db.session.commit()

        return jsonify({'message': 'Subject deleted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500