from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Parent, User, Student, ParentStudentRelationship, Attendance, Grade, Fee
from datetime import datetime, timedelta

parents_bp = Blueprint('parents', __name__)

@parents_bp.route('', methods=['GET'])
@jwt_required()
def get_parents():
    """Get all parents (admin/teacher) or parent's own info"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role in ['admin', 'teacher']:
            # Admin/teacher can see all parents in their school
            parents = Parent.query.filter_by(school_id=user.school_id, is_active=True).all()
            return jsonify({
                'parents': [parent.to_dict() for parent in parents],
                'total': len(parents)
            })
        
        elif user.role == 'parent':
            # Parent sees their own info
            parent = Parent.query.filter_by(user_id=user.id).first()
            if not parent:
                return jsonify({'error': 'Parent profile not found'}), 404
            return jsonify({'parent': parent.to_dict()})
        
        else:
            return jsonify({'error': 'Unauthorized'}), 403
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parents_bp.route('', methods=['POST'])
@jwt_required()
def create_parent():
    """Create a new parent (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'superadmin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'phone_number']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create user account
        parent_user = User(
            username=data['email'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data['phone_number'],
            role='parent',
            school_id=user.school_id,
            created_by_id=user.id,
            is_verified=True
        )
        parent_user.set_password(data.get('password', 'parent123'))  # Default password
        
        db.session.add(parent_user)
        db.session.flush()  # Get the user ID
        
        # Create parent profile
        parent = Parent(
            user_id=parent_user.id,
            school_id=user.school_id,
            title=data.get('title'),
            gender=data.get('gender'),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            national_id=data.get('national_id'),
            address=data.get('address'),
            emergency_contact=data.get('emergency_contact'),
            emergency_contact_name=data.get('emergency_contact_name'),
            occupation=data.get('occupation'),
            employer=data.get('employer'),
            preferred_communication=data.get('preferred_communication', 'sms')
        )
        
        db.session.add(parent)
        db.session.commit()
        
        return jsonify({
            'message': 'Parent created successfully',
            'parent': parent.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@parents_bp.route('/<int:parent_id>', methods=['GET'])
@jwt_required()
def get_parent(parent_id):
    """Get specific parent details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        parent = Parent.query.get(parent_id)
        if not parent:
            return jsonify({'error': 'Parent not found'}), 404
        
        # Check permissions
        if user.role == 'parent' and parent.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        elif user.role in ['admin', 'teacher'] and parent.school_id != user.school_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({'parent': parent.to_dict()})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parents_bp.route('/<int:parent_id>', methods=['PUT'])
@jwt_required()
def update_parent(parent_id):
    """Update parent information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        parent = Parent.query.get(parent_id)
        if not parent:
            return jsonify({'error': 'Parent not found'}), 404
        
        # Check permissions
        if user.role == 'parent' and parent.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        elif user.role in ['admin'] and parent.school_id != user.school_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Update parent fields
        updatable_fields = [
            'title', 'gender', 'address', 'emergency_contact', 'emergency_contact_name',
            'occupation', 'employer', 'work_address', 'work_phone', 'preferred_communication'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(parent, field, data[field])
        
        if 'date_of_birth' in data and data['date_of_birth']:
            parent.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        
        # Update user fields
        if 'first_name' in data:
            parent.user.first_name = data['first_name']
        if 'last_name' in data:
            parent.user.last_name = data['last_name']
        if 'phone_number' in data:
            parent.user.phone_number = data['phone_number']
        
        # Update notification preferences
        if 'notification_preferences' in data:
            current_prefs = parent.notification_preferences or {}
            current_prefs.update(data['notification_preferences'])
            parent.notification_preferences = current_prefs
        
        parent.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Parent updated successfully',
            'parent': parent.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@parents_bp.route('/<int:parent_id>/children', methods=['GET'])
@jwt_required()
def get_parent_children(parent_id):
    """Get children associated with a parent"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        parent = Parent.query.get(parent_id)
        if not parent:
            return jsonify({'error': 'Parent not found'}), 404
        
        # Check permissions
        if user.role == 'parent' and parent.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        elif user.role in ['admin', 'teacher'] and parent.school_id != user.school_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        relationships = ParentStudentRelationship.query.filter_by(
            parent_id=parent_id, is_active=True
        ).all()
        
        children = []
        for rel in relationships:
            student_data = rel.student.to_dict()
            student_data['relationship'] = {
                'type': rel.relationship_type,
                'can_view_grades': rel.can_view_grades,
                'can_view_attendance': rel.can_view_attendance,
                'can_view_fees': rel.can_view_fees,
                'is_emergency_contact': rel.is_emergency_contact
            }
            children.append(student_data)
        
        return jsonify({
            'children': children,
            'total': len(children)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parents_bp.route('/<int:parent_id>/children/<int:student_id>', methods=['POST'])
@jwt_required()
def add_child_to_parent(parent_id, student_id):
    """Associate a child with a parent"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        parent = Parent.query.get(parent_id)
        student = Student.query.get(student_id)
        
        if not parent or not student:
            return jsonify({'error': 'Parent or student not found'}), 404
        
        # Check if relationship already exists
        existing = ParentStudentRelationship.query.filter_by(
            parent_id=parent_id, student_id=student_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Relationship already exists'}), 409
        
        data = request.get_json()
        
        relationship = ParentStudentRelationship(
            parent_id=parent_id,
            student_id=student_id,
            relationship_type=data.get('relationship_type', 'parent'),
            can_view_grades=data.get('can_view_grades', True),
            can_view_attendance=data.get('can_view_attendance', True),
            can_view_fees=data.get('can_view_fees', True),
            can_receive_notifications=data.get('can_receive_notifications', True),
            is_emergency_contact=data.get('is_emergency_contact', False)
        )
        
        db.session.add(relationship)
        db.session.commit()
        
        return jsonify({
            'message': 'Child added to parent successfully',
            'relationship': relationship.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@parents_bp.route('/<int:parent_id>/dashboard', methods=['GET'])
@jwt_required()
def get_parent_dashboard(parent_id):
    """Get parent dashboard with children's overview"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        parent = Parent.query.get(parent_id)
        if not parent:
            return jsonify({'error': 'Parent not found'}), 404
        
        # Check permissions
        if user.role == 'parent' and parent.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        children_overview = []
        
        # Get all children
        relationships = ParentStudentRelationship.query.filter_by(
            parent_id=parent_id, is_active=True
        ).all()
        
        for rel in relationships:
            student = rel.student
            
            # Get recent attendance (last 7 days)
            seven_days_ago = datetime.now() - timedelta(days=7)
            recent_attendance = Attendance.query.filter(
                Attendance.student_id == student.id,
                Attendance.date >= seven_days_ago.date()
            ).all()
            
            attendance_count = len([a for a in recent_attendance if a.status == 'present'])
            attendance_percentage = (attendance_count / len(recent_attendance) * 100) if recent_attendance else 0
            
            # Get recent grades
            recent_grades = Grade.query.filter_by(student_id=student.id).order_by(
                Grade.created_at.desc()
            ).limit(5).all()
            
            # Get fee balance
            fee_balance = student.get_fee_balance()
            
            child_overview = {
                'student': student.to_dict(),
                'attendance': {
                    'percentage_7_days': round(attendance_percentage, 2),
                    'present_days': attendance_count,
                    'total_days': len(recent_attendance)
                },
                'recent_grades': [grade.to_dict() for grade in recent_grades],
                'fee_balance': fee_balance,
                'relationship': rel.to_dict()
            }
            
            children_overview.append(child_overview)
        
        return jsonify({
            'parent': parent.to_dict(),
            'children_overview': children_overview,
            'summary': {
                'total_children': len(children_overview),
                'total_fee_balance': sum(child['fee_balance'] for child in children_overview)
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parents_bp.route('/<int:parent_id>/notifications', methods=['GET'])
@jwt_required()
def get_parent_notifications(parent_id):
    """Get notifications for parent"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        parent = Parent.query.get(parent_id)
        if not parent:
            return jsonify({'error': 'Parent not found'}), 404
        
        # Check permissions
        if user.role == 'parent' and parent.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get messages sent to this parent
        from app.models import Message
        
        messages = Message.query.filter(
            db.or_(
                Message.recipient_id == parent.user_id,
                Message.recipient_groups.contains(['all_parents']),
                Message.recipient_groups.contains([f'parent_{parent.id}'])
            )
        ).order_by(Message.created_at.desc()).limit(50).all()
        
        return jsonify({
            'notifications': [msg.to_dict() for msg in messages],
            'unread_count': len([m for m in messages if not m.is_read])
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parents_bp.route('/<int:parent_id>/child/<int:student_id>/attendance', methods=['GET'])
@jwt_required()
def get_child_attendance(parent_id, student_id):
    """Get child's attendance records"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify parent-child relationship
        relationship = ParentStudentRelationship.query.filter_by(
            parent_id=parent_id, student_id=student_id, is_active=True
        ).first()
        
        if not relationship or not relationship.can_view_attendance:
            return jsonify({'error': 'Unauthorized or no permission'}), 403
        
        # Check if current user is this parent
        if user.role == 'parent':
            parent = Parent.query.filter_by(user_id=user.id).first()
            if not parent or parent.id != parent_id:
                return jsonify({'error': 'Unauthorized'}), 403
        
        # Get attendance records
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Attendance.query.filter_by(student_id=student_id)
        
        if start_date:
            query = query.filter(Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        attendance_records = query.order_by(Attendance.date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'attendance': [record.to_dict() for record in attendance_records.items],
            'pagination': {
                'total': attendance_records.total,
                'pages': attendance_records.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500