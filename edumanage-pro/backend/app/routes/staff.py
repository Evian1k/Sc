from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.staff import Staff
from datetime import datetime
from decimal import Decimal

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/', methods=['GET'])
@jwt_required()
def get_staff():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        position = request.args.get('position', '')
        department = request.args.get('department', '')
        
        query = Staff.query
        
        if search:
            query = query.filter(
                (Staff.first_name.contains(search)) |
                (Staff.last_name.contains(search)) |
                (Staff.staff_id.contains(search))
            )
        
        if position:
            query = query.filter_by(position=position)
        
        if department:
            query = query.filter_by(department=department)
        
        staff_members = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'staff': [staff.to_dict() for staff in staff_members.items],
            'total': staff_members.total,
            'pages': staff_members.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@staff_bp.route('/<int:staff_id>', methods=['GET'])
@jwt_required()
def get_staff_member(staff_id):
    try:
        staff = Staff.query.get_or_404(staff_id)
        return jsonify(staff.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@staff_bp.route('/', methods=['POST'])
@jwt_required()
def create_staff():
    try:
        data = request.get_json()
        
        # Create user account
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            role=data.get('role', 'staff')
        )
        user.set_password(data.get('password', 'staff123'))
        
        db.session.add(user)
        db.session.flush()
        
        # Create staff profile
        staff = Staff(
            user_id=user.id,
            staff_id=data.get('staff_id'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            date_of_birth=datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date(),
            gender=data.get('gender'),
            phone=data.get('phone'),
            address=data.get('address'),
            position=data.get('position'),
            department=data.get('department'),
            salary=Decimal(str(data.get('salary', 0))),
            qualification=data.get('qualification'),
            emergency_contact=data.get('emergency_contact'),
            emergency_phone=data.get('emergency_phone')
        )
        
        if 'hire_date' in data:
            staff.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
        
        db.session.add(staff)
        db.session.commit()
        
        return jsonify({'message': 'Staff member created successfully', 'staff': staff.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@staff_bp.route('/<int:staff_id>', methods=['PUT'])
@jwt_required()
def update_staff(staff_id):
    try:
        staff = Staff.query.get_or_404(staff_id)
        data = request.get_json()
        
        # Update staff fields
        for field in ['first_name', 'last_name', 'gender', 'phone', 'address', 
                     'position', 'department', 'qualification', 'emergency_contact', 'emergency_phone']:
            if field in data:
                setattr(staff, field, data[field])
        
        if 'date_of_birth' in data:
            staff.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        
        if 'hire_date' in data:
            staff.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
        
        if 'salary' in data:
            staff.salary = Decimal(str(data['salary']))
        
        # Update user fields if provided
        if 'email' in data:
            staff.user.email = data['email']
        
        if 'role' in data:
            staff.user.role = data['role']
        
        db.session.commit()
        
        return jsonify({'message': 'Staff member updated successfully', 'staff': staff.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@staff_bp.route('/<int:staff_id>', methods=['DELETE'])
@jwt_required()
def delete_staff(staff_id):
    try:
        staff = Staff.query.get_or_404(staff_id)
        user = staff.user
        
        db.session.delete(staff)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Staff member deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@staff_bp.route('/positions', methods=['GET'])
@jwt_required()
def get_positions():
    try:
        positions = db.session.query(Staff.position).distinct().all()
        return jsonify([pos[0] for pos in positions if pos[0]]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@staff_bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    try:
        departments = db.session.query(Staff.department).distinct().all()
        return jsonify([dept[0] for dept in departments if dept[0]]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@staff_bp.route('/teachers', methods=['GET'])
@jwt_required()
def get_teachers():
    try:
        teachers = Staff.query.filter(Staff.position.like('%teacher%')).filter_by(is_active=True).all()
        return jsonify([teacher.to_dict() for teacher in teachers]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500