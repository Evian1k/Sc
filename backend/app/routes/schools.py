from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import School, User
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime

schools_bp = Blueprint('schools', __name__)
limiter = Limiter(key_func=get_remote_address)

@schools_bp.route('', methods=['GET'])
@jwt_required()
def get_schools():
    """Get all schools (superadmin only) or current user's school"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Superadmin can see all schools
        if user.role == 'superadmin':
            schools = School.query.all()
            return jsonify({
                'schools': [school.to_dict() for school in schools],
                'total': len(schools)
            })
        
        # Other users see only their school
        if user.school_id:
            school = School.query.get(user.school_id)
            return jsonify({'school': school.to_dict() if school else None})
        
        return jsonify({'error': 'No school assigned'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@schools_bp.route('', methods=['POST'])
@jwt_required()
def create_school():
    """Create a new school (superadmin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'superadmin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'short_name', 'code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if code already exists
        if School.query.filter_by(code=data['code']).first():
            return jsonify({'error': 'School code already exists'}), 409
        
        school = School(
            name=data['name'],
            short_name=data['short_name'],
            code=data['code'],
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            country=data.get('country', 'Kenya'),
            postal_code=data.get('postal_code'),
            website=data.get('website'),
            primary_color=data.get('primary_color', '#3B82F6'),
            secondary_color=data.get('secondary_color', '#10B981'),
            academic_year_start=datetime.strptime(data['academic_year_start'], '%Y-%m-%d').date() if data.get('academic_year_start') else None,
            academic_year_end=datetime.strptime(data['academic_year_end'], '%Y-%m-%d').date() if data.get('academic_year_end') else None,
            current_term=data.get('current_term'),
            total_terms=data.get('total_terms', 3),
            subscription_type=data.get('subscription_type', 'free'),
            max_students=data.get('max_students', 100),
            max_staff=data.get('max_staff', 20)
        )
        
        db.session.add(school)
        db.session.commit()
        
        return jsonify({
            'message': 'School created successfully',
            'school': school.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@schools_bp.route('/<int:school_id>', methods=['GET'])
@jwt_required()
def get_school(school_id):
    """Get specific school details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        school = School.query.get(school_id)
        if not school:
            return jsonify({'error': 'School not found'}), 404
        
        # Check permissions
        if user.role != 'superadmin' and user.school_id != school_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({'school': school.to_dict()})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@schools_bp.route('/<int:school_id>', methods=['PUT'])
@jwt_required()
def update_school(school_id):
    """Update school information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        school = School.query.get(school_id)
        if not school:
            return jsonify({'error': 'School not found'}), 404
        
        # Check permissions (superadmin or school admin)
        if user.role not in ['superadmin', 'admin'] or (user.role == 'admin' and user.school_id != school_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Update fields
        updatable_fields = [
            'name', 'short_name', 'email', 'phone', 'address', 'city', 'state',
            'country', 'postal_code', 'website', 'primary_color', 'secondary_color',
            'current_term', 'total_terms'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(school, field, data[field])
        
        # Handle date fields
        if 'academic_year_start' in data and data['academic_year_start']:
            school.academic_year_start = datetime.strptime(data['academic_year_start'], '%Y-%m-%d').date()
        
        if 'academic_year_end' in data and data['academic_year_end']:
            school.academic_year_end = datetime.strptime(data['academic_year_end'], '%Y-%m-%d').date()
        
        # Superadmin only fields
        if user.role == 'superadmin':
            superadmin_fields = ['subscription_type', 'max_students', 'max_staff', 'is_active']
            for field in superadmin_fields:
                if field in data:
                    setattr(school, field, data[field])
        
        school.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'School updated successfully',
            'school': school.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@schools_bp.route('/<int:school_id>/settings', methods=['GET'])
@jwt_required()
def get_school_settings(school_id):
    """Get school settings"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        school = School.query.get(school_id)
        if not school:
            return jsonify({'error': 'School not found'}), 404
        
        # Check permissions
        if user.role not in ['superadmin', 'admin'] or (user.role == 'admin' and user.school_id != school_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'settings': school.settings,
            'features_enabled': school.features_enabled
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@schools_bp.route('/<int:school_id>/settings', methods=['PUT'])
@jwt_required()
def update_school_settings(school_id):
    """Update school settings"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        school = School.query.get(school_id)
        if not school:
            return jsonify({'error': 'School not found'}), 404
        
        # Check permissions
        if user.role not in ['superadmin', 'admin'] or (user.role == 'admin' and user.school_id != school_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if 'settings' in data:
            # Merge with existing settings
            current_settings = school.settings or {}
            current_settings.update(data['settings'])
            school.settings = current_settings
        
        if 'features_enabled' in data and user.role == 'superadmin':
            # Only superadmin can change features
            current_features = school.features_enabled or {}
            current_features.update(data['features_enabled'])
            school.features_enabled = current_features
        
        school.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Settings updated successfully',
            'settings': school.settings,
            'features_enabled': school.features_enabled
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@schools_bp.route('/<int:school_id>/analytics', methods=['GET'])
@jwt_required()
def get_school_analytics(school_id):
    """Get school analytics and statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        school = School.query.get(school_id)
        if not school:
            return jsonify({'error': 'School not found'}), 404
        
        # Check permissions
        if user.role not in ['superadmin', 'admin'] or (user.role == 'admin' and user.school_id != school_id):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get basic stats
        stats = school.get_stats()
        
        # Add more detailed analytics
        from app.models import Student, Staff, Fee, Attendance
        
        # Student analytics
        total_students = Student.query.filter_by(school_id=school_id, is_active=True).count()
        male_students = Student.query.filter_by(school_id=school_id, is_active=True, gender='Male').count()
        female_students = Student.query.filter_by(school_id=school_id, is_active=True, gender='Female').count()
        
        # Staff analytics
        total_staff = Staff.query.filter_by(school_id=school_id, is_active=True).count()
        teachers = Staff.query.filter_by(school_id=school_id, is_active=True, position='Teacher').count()
        
        # Fee analytics
        total_fees_due = db.session.query(db.func.sum(Fee.amount)).join(Student).filter(
            Student.school_id == school_id, Fee.status == 'pending'
        ).scalar() or 0
        
        total_fees_paid = db.session.query(db.func.sum(Fee.amount_paid)).join(Student).filter(
            Student.school_id == school_id
        ).scalar() or 0
        
        # Attendance analytics (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        total_attendance_records = db.session.query(Attendance).join(Student).filter(
            Student.school_id == school_id,
            Attendance.date >= thirty_days_ago.date()
        ).count()
        
        present_records = db.session.query(Attendance).join(Student).filter(
            Student.school_id == school_id,
            Attendance.date >= thirty_days_ago.date(),
            Attendance.status == 'present'
        ).count()
        
        attendance_rate = (present_records / total_attendance_records * 100) if total_attendance_records > 0 else 0
        
        analytics = {
            'basic_stats': stats,
            'student_analytics': {
                'total_students': total_students,
                'male_students': male_students,
                'female_students': female_students,
                'gender_distribution': {
                    'male_percentage': (male_students / total_students * 100) if total_students > 0 else 0,
                    'female_percentage': (female_students / total_students * 100) if total_students > 0 else 0
                }
            },
            'staff_analytics': {
                'total_staff': total_staff,
                'teachers': teachers,
                'other_staff': total_staff - teachers
            },
            'financial_analytics': {
                'total_fees_due': float(total_fees_due),
                'total_fees_paid': float(total_fees_paid),
                'collection_rate': (total_fees_paid / (total_fees_due + total_fees_paid) * 100) if (total_fees_due + total_fees_paid) > 0 else 0
            },
            'attendance_analytics': {
                'attendance_rate_30_days': round(attendance_rate, 2),
                'total_records': total_attendance_records,
                'present_records': present_records
            }
        }
        
        return jsonify({'analytics': analytics})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500