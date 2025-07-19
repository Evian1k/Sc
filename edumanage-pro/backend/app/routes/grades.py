from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.grade import Grade
from app.models.student import Student
from app.models.subject import Subject
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func

grades_bp = Blueprint('grades', __name__)

@grades_bp.route('/', methods=['GET'])
@jwt_required()
def get_grades():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        student_id = request.args.get('student_id', type=int)
        subject_id = request.args.get('subject_id', type=int)
        assessment_type = request.args.get('assessment_type')
        semester = request.args.get('semester')
        academic_year = request.args.get('academic_year')
        
        query = Grade.query.join(Student).join(Subject)
        
        if student_id:
            query = query.filter(Grade.student_id == student_id)
        
        if subject_id:
            query = query.filter(Grade.subject_id == subject_id)
        
        if assessment_type:
            query = query.filter(Grade.assessment_type == assessment_type)
        
        if semester:
            query = query.filter(Grade.semester == semester)
        
        if academic_year:
            query = query.filter(Grade.academic_year == academic_year)
        
        grades = query.order_by(Grade.date_assessed.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'grades': [grade.to_dict() for grade in grades.items],
            'total': grades.total,
            'pages': grades.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grades_bp.route('/<int:grade_id>', methods=['GET'])
@jwt_required()
def get_grade(grade_id):
    try:
        grade = Grade.query.get_or_404(grade_id)
        return jsonify(grade.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grades_bp.route('/', methods=['POST'])
@jwt_required()
def create_grade():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        grade = Grade(
            student_id=data.get('student_id'),
            subject_id=data.get('subject_id'),
            assessment_type=data.get('assessment_type'),
            assessment_name=data.get('assessment_name'),
            marks_obtained=Decimal(str(data.get('marks_obtained'))),
            total_marks=Decimal(str(data.get('total_marks'))),
            semester=data.get('semester'),
            academic_year=data.get('academic_year'),
            teacher_id=user_id,
            comments=data.get('comments', '')
        )
        
        if 'date_assessed' in data:
            grade.date_assessed = datetime.strptime(data['date_assessed'], '%Y-%m-%d').date()
        
        # Calculate percentage and grade letter
        grade.calculate_percentage()
        grade.calculate_grade_letter()
        
        db.session.add(grade)
        db.session.commit()
        
        return jsonify({'message': 'Grade created successfully', 'grade': grade.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@grades_bp.route('/<int:grade_id>', methods=['PUT'])
@jwt_required()
def update_grade(grade_id):
    try:
        grade = Grade.query.get_or_404(grade_id)
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Update fields
        for field in ['assessment_type', 'assessment_name', 'semester', 'academic_year', 'comments']:
            if field in data:
                setattr(grade, field, data[field])
        
        if 'marks_obtained' in data:
            grade.marks_obtained = Decimal(str(data['marks_obtained']))
        
        if 'total_marks' in data:
            grade.total_marks = Decimal(str(data['total_marks']))
        
        if 'date_assessed' in data:
            grade.date_assessed = datetime.strptime(data['date_assessed'], '%Y-%m-%d').date()
        
        grade.teacher_id = user_id
        
        # Recalculate percentage and grade letter
        grade.calculate_percentage()
        grade.calculate_grade_letter()
        
        db.session.commit()
        
        return jsonify({'message': 'Grade updated successfully', 'grade': grade.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@grades_bp.route('/<int:grade_id>', methods=['DELETE'])
@jwt_required()
def delete_grade(grade_id):
    try:
        grade = Grade.query.get_or_404(grade_id)
        db.session.delete(grade)
        db.session.commit()
        
        return jsonify({'message': 'Grade deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@grades_bp.route('/subjects', methods=['GET'])
@jwt_required()
def get_subjects():
    try:
        subjects = Subject.query.filter_by(is_active=True).all()
        return jsonify([subject.to_dict() for subject in subjects]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grades_bp.route('/subjects', methods=['POST'])
@jwt_required()
def create_subject():
    try:
        data = request.get_json()
        
        subject = Subject(
            name=data.get('name'),
            code=data.get('code'),
            description=data.get('description', ''),
            credits=data.get('credits', 3)
        )
        
        db.session.add(subject)
        db.session.commit()
        
        return jsonify({'message': 'Subject created successfully', 'subject': subject.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@grades_bp.route('/bulk-create', methods=['POST'])
@jwt_required()
def bulk_create_grades():
    try:
        data = request.get_json()
        grades_data = data.get('grades', [])
        user_id = get_jwt_identity()
        
        created_grades = []
        errors = []
        
        for idx, grade_data in enumerate(grades_data):
            try:
                grade = Grade(
                    student_id=grade_data.get('student_id'),
                    subject_id=grade_data.get('subject_id'),
                    assessment_type=grade_data.get('assessment_type'),
                    assessment_name=grade_data.get('assessment_name'),
                    marks_obtained=Decimal(str(grade_data.get('marks_obtained'))),
                    total_marks=Decimal(str(grade_data.get('total_marks'))),
                    semester=grade_data.get('semester'),
                    academic_year=grade_data.get('academic_year'),
                    teacher_id=user_id,
                    comments=grade_data.get('comments', '')
                )
                
                if 'date_assessed' in grade_data:
                    grade.date_assessed = datetime.strptime(grade_data['date_assessed'], '%Y-%m-%d').date()
                
                grade.calculate_percentage()
                grade.calculate_grade_letter()
                
                db.session.add(grade)
                created_grades.append(grade.to_dict())
                
            except Exception as e:
                errors.append({'row': idx + 1, 'error': str(e)})
        
        if not errors:
            db.session.commit()
        else:
            db.session.rollback()
        
        return jsonify({
            'message': f'Created {len(created_grades)} grades successfully',
            'created_grades': created_grades,
            'errors': errors
        }), 201 if not errors else 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@grades_bp.route('/student/<int:student_id>/report', methods=['GET'])
@jwt_required()
def student_grade_report(student_id):
    try:
        semester = request.args.get('semester')
        academic_year = request.args.get('academic_year')
        
        query = Grade.query.filter_by(student_id=student_id).join(Subject)
        
        if semester:
            query = query.filter(Grade.semester == semester)
        
        if academic_year:
            query = query.filter(Grade.academic_year == academic_year)
        
        grades = query.all()
        
        # Calculate overall statistics
        if grades:
            total_percentage = sum(float(grade.percentage) for grade in grades if grade.percentage)
            average_percentage = total_percentage / len(grades)
            
            # Calculate GPA (assuming 4.0 scale)
            grade_points = {
                'A+': 4.0, 'A': 4.0, 'B+': 3.5, 'B': 3.0,
                'C+': 2.5, 'C': 2.0, 'D': 1.0, 'F': 0.0
            }
            
            total_credits = sum(grade.subject.credits for grade in grades)
            weighted_points = sum(grade_points.get(grade.grade_letter, 0) * grade.subject.credits for grade in grades)
            gpa = weighted_points / total_credits if total_credits > 0 else 0
        else:
            average_percentage = 0
            gpa = 0
        
        # Group grades by subject
        subject_grades = {}
        for grade in grades:
            subject_name = grade.subject.name
            if subject_name not in subject_grades:
                subject_grades[subject_name] = []
            subject_grades[subject_name].append(grade.to_dict())
        
        return jsonify({
            'student_id': student_id,
            'grades': [grade.to_dict() for grade in grades],
            'subject_grades': subject_grades,
            'statistics': {
                'total_assessments': len(grades),
                'average_percentage': round(average_percentage, 2),
                'gpa': round(gpa, 2)
            },
            'filters': {
                'semester': semester,
                'academic_year': academic_year
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@grades_bp.route('/class/<int:class_id>/report', methods=['GET'])
@jwt_required()
def class_grade_report(class_id):
    try:
        semester = request.args.get('semester')
        academic_year = request.args.get('academic_year')
        subject_id = request.args.get('subject_id', type=int)
        
        query = db.session.query(
            Student.id,
            Student.first_name,
            Student.last_name,
            Student.student_id,
            func.avg(Grade.percentage).label('average_percentage'),
            func.count(Grade.id).label('total_assessments')
        ).join(
            Grade, Student.id == Grade.student_id
        ).filter(
            Student.class_id == class_id
        )
        
        if semester:
            query = query.filter(Grade.semester == semester)
        
        if academic_year:
            query = query.filter(Grade.academic_year == academic_year)
        
        if subject_id:
            query = query.filter(Grade.subject_id == subject_id)
        
        results = query.group_by(Student.id).all()
        
        report_data = []
        for result in results:
            report_data.append({
                'student_id': result.id,
                'student_name': f"{result.first_name} {result.last_name}",
                'student_number': result.student_id,
                'average_percentage': round(float(result.average_percentage), 2) if result.average_percentage else 0,
                'total_assessments': result.total_assessments
            })
        
        return jsonify({
            'class_id': class_id,
            'report': report_data,
            'filters': {
                'semester': semester,
                'academic_year': academic_year,
                'subject_id': subject_id
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500