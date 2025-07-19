from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.student import Student
from app.models.class_model import Class
from datetime import datetime

students_bp = Blueprint('students', __name__)

@students_bp.route('/', methods=['GET'])
@jwt_required()
def get_students():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        class_id = request.args.get('class_id', type=int)
        
        query = Student.query
        
        if search:
            query = query.filter(
                (Student.first_name.contains(search)) |
                (Student.last_name.contains(search)) |
                (Student.student_id.contains(search))
            )
        
        if class_id:
            query = query.filter_by(class_id=class_id)
        
        students = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'students': [student.to_dict() for student in students.items],
            'total': students.total,
            'pages': students.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@students_bp.route('/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        return jsonify(student.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@students_bp.route('/', methods=['POST'])
@jwt_required()
def create_student():
    try:
        data = request.get_json()
        
        # Create user account
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            role='student'
        )
        user.set_password(data.get('password', 'student123'))
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create student profile
        student = Student(
            user_id=user.id,
            student_id=data.get('student_id'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            date_of_birth=datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date(),
            gender=data.get('gender'),
            phone=data.get('phone'),
            address=data.get('address'),
            class_id=data.get('class_id'),
            parent_name=data.get('parent_name'),
            parent_phone=data.get('parent_phone'),
            parent_email=data.get('parent_email')
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({'message': 'Student created successfully', 'student': student.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@students_bp.route('/<int:student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        data = request.get_json()
        
        # Update student fields
        for field in ['first_name', 'last_name', 'gender', 'phone', 'address', 
                     'class_id', 'parent_name', 'parent_phone', 'parent_email']:
            if field in data:
                setattr(student, field, data[field])
        
        if 'date_of_birth' in data:
            student.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        
        # Update user fields if provided
        if 'email' in data:
            student.user.email = data['email']
        
        db.session.commit()
        
        return jsonify({'message': 'Student updated successfully', 'student': student.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@students_bp.route('/<int:student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        user = student.user
        
        db.session.delete(student)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Student deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@students_bp.route('/classes', methods=['GET'])
@jwt_required()
def get_classes():
    try:
        classes = Class.query.filter_by(is_active=True).all()
        return jsonify([cls.to_dict() for cls in classes]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@students_bp.route('/bulk-import', methods=['POST'])
@jwt_required()
def bulk_import_students():
    try:
        data = request.get_json()
        students_data = data.get('students', [])
        
        created_students = []
        errors = []
        
        for idx, student_data in enumerate(students_data):
            try:
                # Create user account
                user = User(
                    username=student_data.get('username'),
                    email=student_data.get('email'),
                    role='student'
                )
                user.set_password(student_data.get('password', 'student123'))
                
                db.session.add(user)
                db.session.flush()
                
                # Create student profile
                student = Student(
                    user_id=user.id,
                    student_id=student_data.get('student_id'),
                    first_name=student_data.get('first_name'),
                    last_name=student_data.get('last_name'),
                    date_of_birth=datetime.strptime(student_data.get('date_of_birth'), '%Y-%m-%d').date(),
                    gender=student_data.get('gender'),
                    phone=student_data.get('phone'),
                    address=student_data.get('address'),
                    class_id=student_data.get('class_id'),
                    parent_name=student_data.get('parent_name'),
                    parent_phone=student_data.get('parent_phone'),
                    parent_email=student_data.get('parent_email')
                )
                
                db.session.add(student)
                created_students.append(student.to_dict())
                
            except Exception as e:
                errors.append({'row': idx + 1, 'error': str(e)})
        
        if not errors:
            db.session.commit()
        else:
            db.session.rollback()
        
        return jsonify({
            'message': f'Imported {len(created_students)} students successfully',
            'created_students': created_students,
            'errors': errors
        }), 201 if not errors else 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500