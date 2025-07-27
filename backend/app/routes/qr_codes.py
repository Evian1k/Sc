from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Student, Class, Event
from app.services.qr_service import qr_service

qr_bp = Blueprint('qr', __name__)

@qr_bp.route('/student/<int:student_id>/generate', methods=['POST'])
@jwt_required()
def generate_student_qr(student_id):
    """Generate QR code for student attendance"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        student = Student.query.get(student_id)
        if not student or student.school_id != user.school_id:
            return jsonify({'error': 'Student not found'}), 404
        
        data = request.get_json() or {}
        valid_hours = data.get('valid_hours', 24)
        
        result = qr_service.generate_student_qr_code(
            student_id, student.school_id, valid_hours
        )
        
        if result['success']:
            # Generate branded QR code with student info
            student_info = {
                'name': student.full_name,
                'student_id': student.student_id,
                'class': student.class_enrolled.name if student.class_enrolled else 'N/A'
            }
            
            branded_result = qr_service.generate_branded_qr_code(
                result['qr_token'],
                student_info=student_info
            )
            
            if branded_result['success']:
                result['branded_qr_image'] = branded_result['qr_image_base64']
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qr_bp.route('/class/<int:class_id>/generate', methods=['POST'])
@jwt_required()
def generate_class_qr(class_id):
    """Generate QR code for class attendance"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        class_obj = Class.query.get(class_id)
        if not class_obj or class_obj.school_id != user.school_id:
            return jsonify({'error': 'Class not found'}), 404
        
        data = request.get_json() or {}
        valid_minutes = data.get('valid_minutes', 60)
        
        result = qr_service.generate_class_qr_code(
            class_id, class_obj.school_id, valid_minutes
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qr_bp.route('/event/<int:event_id>/generate', methods=['POST'])
@jwt_required()
def generate_event_qr(event_id):
    """Generate QR code for event attendance"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        event = Event.query.get(event_id)
        if not event or event.school_id != user.school_id:
            return jsonify({'error': 'Event not found'}), 404
        
        data = request.get_json() or {}
        valid_hours = data.get('valid_hours', 12)
        
        result = qr_service.generate_event_qr_code(
            event_id, event.school_id, valid_hours
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qr_bp.route('/scan', methods=['POST'])
@jwt_required()
def scan_qr_code():
    """Process QR code scan for attendance"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        qr_token = data.get('qr_token')
        
        if not qr_token:
            return jsonify({'error': 'QR token is required'}), 400
        
        result = qr_service.process_attendance_scan(qr_token, user.id)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qr_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_qr_code():
    """Verify QR code without processing attendance"""
    try:
        data = request.get_json()
        qr_token = data.get('qr_token')
        
        if not qr_token:
            return jsonify({'error': 'QR token is required'}), 400
        
        result = qr_service.verify_qr_code(qr_token)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qr_bp.route('/bulk-generate/students', methods=['POST'])
@jwt_required()
def bulk_generate_student_qrs():
    """Generate QR codes for multiple students"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        student_ids = data.get('student_ids', [])
        
        if not student_ids:
            return jsonify({'error': 'Student IDs are required'}), 400
        
        # Verify all students belong to the same school
        students = Student.query.filter(
            Student.id.in_(student_ids),
            Student.school_id == user.school_id
        ).all()
        
        if len(students) != len(student_ids):
            return jsonify({'error': 'Some students not found or unauthorized'}), 404
        
        result = qr_service.bulk_generate_student_qr_codes(
            student_ids, user.school_id
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500