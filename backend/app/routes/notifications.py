from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Student, Parent, Staff
from app.services.notification_service import notification_service
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/send/sms', methods=['POST'])
@jwt_required()
def send_sms():
    """Send SMS notification"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('phone_number') or not data.get('message'):
            return jsonify({'error': 'Phone number and message are required'}), 400
        
        result = notification_service.send_sms_africastalking(
            data['phone_number'],
            data['message'],
            user.school_id
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/send/email', methods=['POST'])
@jwt_required()
def send_email():
    """Send email notification"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('recipients') or not data.get('subject') or not data.get('content'):
            return jsonify({'error': 'Recipients, subject, and content are required'}), 400
        
        result = notification_service.send_email(
            data['recipients'],
            data['subject'],
            data['content'],
            data.get('html_content'),
            user.school_id
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/send/broadcast', methods=['POST'])
@jwt_required()
def send_broadcast():
    """Send broadcast message to multiple recipients"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['recipient_groups', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        result = notification_service.send_broadcast_message(
            user.school_id,
            data['recipient_groups'],
            data['subject'],
            data['message'],
            data.get('channels', ['sms', 'email'])
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/attendance/alert', methods=['POST'])
@jwt_required()
def send_attendance_alert():
    """Send attendance alert to parents"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if not data.get('student_id') or not data.get('status'):
            return jsonify({'error': 'Student ID and status are required'}), 400
        
        result = notification_service.send_attendance_alert(
            data['student_id'],
            data['status'],
            datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else None
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/fee/reminder', methods=['POST'])
@jwt_required()
def send_fee_reminder():
    """Send fee payment reminder"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'accountant']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        required_fields = ['student_id', 'amount_due', 'due_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        result = notification_service.send_fee_reminder(
            data['student_id'],
            data['amount_due'],
            datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/exam/results', methods=['POST'])
@jwt_required()
def send_exam_results():
    """Send exam results notification"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        required_fields = ['student_id', 'exam_name', 'subject_results']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        result = notification_service.send_exam_result_notification(
            data['student_id'],
            data['exam_name'],
            data['subject_results']
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_notification_templates():
    """Get notification templates"""
    try:
        templates = {
            'attendance_alert': {
                'present': 'Dear Parent, your child {student_name} has arrived safely at {school_name} on {date}.',
                'absent': 'Dear Parent, your child {student_name} was marked absent on {date}. Please contact {school_name} if this is incorrect.'
            },
            'fee_reminder': 'Dear Parent, this is a reminder that {student_name} has an outstanding fee balance of {currency} {amount} due on {due_date}. Please make payment at your earliest convenience. - {school_name}',
            'exam_notification': 'Dear Parent/Student, the {exam_name} has been scheduled from {start_date} to {end_date}. Please check the timetable for details. - {school_name}',
            'general_announcement': 'Dear {recipient_type}, {message} - {school_name}'
        }
        
        return jsonify({'templates': templates})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/recipient-groups', methods=['GET'])
@jwt_required()
def get_recipient_groups():
    """Get available recipient groups for broadcasts"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get classes for this school
        from app.models import Class
        classes = Class.query.filter_by(school_id=user.school_id, is_active=True).all()
        
        groups = {
            'all': [
                {'id': 'all_students', 'name': 'All Students'},
                {'id': 'all_parents', 'name': 'All Parents'},
                {'id': 'all_staff', 'name': 'All Staff'},
                {'id': 'all_teachers', 'name': 'All Teachers'}
            ],
            'classes': [
                {'id': f'class_{class_obj.id}', 'name': f'Class {class_obj.name}'}
                for class_obj in classes
            ],
            'roles': [
                {'id': 'administrators', 'name': 'Administrators'},
                {'id': 'teachers', 'name': 'Teachers'},
                {'id': 'accountants', 'name': 'Accountants'}
            ]
        }
        
        return jsonify({'recipient_groups': groups})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/history', methods=['GET'])
@jwt_required()
def get_notification_history():
    """Get notification history"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get messages sent by this user
        from app.models import Message
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Message.query.filter_by(
            sender_id=user.id,
            school_id=user.school_id
        ).order_by(Message.created_at.desc())
        
        messages = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'messages': [msg.to_dict() for msg in messages.items],
            'pagination': {
                'total': messages.total,
                'pages': messages.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_notification_settings():
    """Get notification settings for the school"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        from app.models import School
        school = School.query.get(user.school_id)
        
        if not school:
            return jsonify({'error': 'School not found'}), 404
        
        settings = {
            'sms_enabled': school.is_feature_enabled('sms_notifications'),
            'email_enabled': school.is_feature_enabled('email_notifications'),
            'whatsapp_enabled': school.is_feature_enabled('whatsapp_notifications'),
            'auto_attendance_alerts': school.get_setting('notification_preferences', {}).get('attendance_alerts', True),
            'auto_fee_reminders': school.get_setting('notification_preferences', {}).get('fee_reminders', True),
            'auto_exam_notifications': school.get_setting('notification_preferences', {}).get('exam_notifications', True)
        }
        
        return jsonify({'settings': settings})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_notification_settings():
    """Update notification settings"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        from app.models import School
        school = School.query.get(user.school_id)
        
        if not school:
            return jsonify({'error': 'School not found'}), 404
        
        data = request.get_json()
        
        # Update notification preferences in school settings
        current_settings = school.settings or {}
        notification_prefs = current_settings.get('notification_preferences', {})
        
        if 'auto_attendance_alerts' in data:
            notification_prefs['attendance_alerts'] = data['auto_attendance_alerts']
        if 'auto_fee_reminders' in data:
            notification_prefs['fee_reminders'] = data['auto_fee_reminders']
        if 'auto_exam_notifications' in data:
            notification_prefs['exam_notifications'] = data['auto_exam_notifications']
        
        current_settings['notification_preferences'] = notification_prefs
        school.settings = current_settings
        
        db.session.commit()
        
        return jsonify({
            'message': 'Notification settings updated successfully',
            'settings': notification_prefs
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500