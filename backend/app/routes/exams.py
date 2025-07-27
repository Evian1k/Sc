from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Exam, ExamSchedule, ExamResult, User, Student, Subject, Class, Staff
from datetime import datetime

exams_bp = Blueprint('exams', __name__)

@exams_bp.route('', methods=['GET'])
@jwt_required()
def get_exams():
    """Get all exams for the school"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Filter by school
        exams = Exam.query.filter_by(school_id=user.school_id).all()
        
        # Filter by user role
        if user.role == 'student':
            # Students see only published exams for their class
            student = Student.query.filter_by(user_id=user.id).first()
            if student and student.class_id:
                exam_ids = [es.exam_id for es in ExamSchedule.query.filter_by(class_id=student.class_id).all()]
                exams = [exam for exam in exams if exam.id in exam_ids and exam.is_published]
        
        elif user.role == 'teacher':
            # Teachers see exams they're assigned to or all if admin
            staff = Staff.query.filter_by(user_id=user.id).first()
            if staff and staff.position != 'Administrator':
                exam_ids = [es.exam_id for es in ExamSchedule.query.filter_by(teacher_id=staff.id).all()]
                exams = [exam for exam in exams if exam.id in exam_ids]
        
        return jsonify({
            'exams': [exam.to_dict() for exam in exams],
            'total': len(exams)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exams_bp.route('', methods=['POST'])
@jwt_required()
def create_exam():
    """Create a new exam"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'exam_type', 'academic_year', 'term', 'start_date', 'end_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        exam = Exam(
            school_id=user.school_id,
            name=data['name'],
            description=data.get('description'),
            exam_type=data['exam_type'],
            academic_year=data['academic_year'],
            term=data['term'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            registration_deadline=datetime.strptime(data['registration_deadline'], '%Y-%m-%d').date() if data.get('registration_deadline') else None,
            results_release_date=datetime.strptime(data['results_release_date'], '%Y-%m-%d').date() if data.get('results_release_date') else None,
            total_marks=data.get('total_marks', 100),
            passing_marks=data.get('passing_marks', 50),
            grading_scale=data.get('grading_scale', 'A-F'),
            instructions=data.get('instructions'),
            rules=data.get('rules'),
            created_by_id=user.id
        )
        
        db.session.add(exam)
        db.session.commit()
        
        return jsonify({
            'message': 'Exam created successfully',
            'exam': exam.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exams_bp.route('/<int:exam_id>', methods=['GET'])
@jwt_required()
def get_exam(exam_id):
    """Get specific exam details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        exam = Exam.query.get(exam_id)
        if not exam or exam.school_id != user.school_id:
            return jsonify({'error': 'Exam not found'}), 404
        
        # Check permissions for students
        if user.role == 'student' and not exam.is_published:
            return jsonify({'error': 'Exam not available'}), 403
        
        return jsonify({'exam': exam.to_dict()})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exams_bp.route('/<int:exam_id>', methods=['PUT'])
@jwt_required()
def update_exam(exam_id):
    """Update exam information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        exam = Exam.query.get(exam_id)
        if not exam or exam.school_id != user.school_id:
            return jsonify({'error': 'Exam not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        updatable_fields = [
            'name', 'description', 'exam_type', 'academic_year', 'term',
            'total_marks', 'passing_marks', 'grading_scale', 'instructions', 'rules'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(exam, field, data[field])
        
        # Handle date fields
        date_fields = ['start_date', 'end_date', 'registration_deadline', 'results_release_date']
        for field in date_fields:
            if field in data and data[field]:
                setattr(exam, field, datetime.strptime(data[field], '%Y-%m-%d').date())
        
        exam.updated_by_id = user.id
        exam.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Exam updated successfully',
            'exam': exam.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exams_bp.route('/<int:exam_id>/publish', methods=['POST'])
@jwt_required()
def publish_exam(exam_id):
    """Publish an exam"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        exam = Exam.query.get(exam_id)
        if not exam or exam.school_id != user.school_id:
            return jsonify({'error': 'Exam not found'}), 404
        
        exam.is_published = True
        exam.status = 'scheduled'
        exam.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Send notifications to students and parents
        from app.services.notification_service import notification_service
        notification_service.send_broadcast_message(
            user.school_id,
            ['all_students', 'all_parents'],
            f'New Exam Scheduled: {exam.name}',
            f'A new exam "{exam.name}" has been scheduled from {exam.start_date} to {exam.end_date}. Please check the timetable for details.'
        )
        
        return jsonify({
            'message': 'Exam published successfully',
            'exam': exam.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exams_bp.route('/<int:exam_id>/schedules', methods=['GET'])
@jwt_required()
def get_exam_schedules(exam_id):
    """Get exam schedules for an exam"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        exam = Exam.query.get(exam_id)
        if not exam or exam.school_id != user.school_id:
            return jsonify({'error': 'Exam not found'}), 404
        
        schedules = ExamSchedule.query.filter_by(exam_id=exam_id).all()
        
        # Filter by user role
        if user.role == 'student':
            student = Student.query.filter_by(user_id=user.id).first()
            if student:
                schedules = [s for s in schedules if s.class_id == student.class_id]
        
        elif user.role == 'teacher':
            staff = Staff.query.filter_by(user_id=user.id).first()
            if staff and staff.position != 'Administrator':
                schedules = [s for s in schedules if s.teacher_id == staff.id]
        
        return jsonify({
            'schedules': [schedule.to_dict() for schedule in schedules],
            'total': len(schedules)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exams_bp.route('/<int:exam_id>/schedules', methods=['POST'])
@jwt_required()
def create_exam_schedule(exam_id):
    """Create an exam schedule"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        exam = Exam.query.get(exam_id)
        if not exam or exam.school_id != user.school_id:
            return jsonify({'error': 'Exam not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['subject_id', 'class_id', 'exam_date', 'start_time', 'end_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Calculate duration
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        start_datetime = datetime.combine(datetime.today(), start_time)
        end_datetime = datetime.combine(datetime.today(), end_time)
        duration_minutes = int((end_datetime - start_datetime).total_seconds() / 60)
        
        schedule = ExamSchedule(
            exam_id=exam_id,
            subject_id=data['subject_id'],
            class_id=data['class_id'],
            teacher_id=data.get('teacher_id'),
            exam_date=datetime.strptime(data['exam_date'], '%Y-%m-%d').date(),
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            venue=data.get('venue'),
            room_number=data.get('room_number'),
            seating_arrangement=data.get('seating_arrangement', 'alphabetical'),
            max_students=data.get('max_students'),
            total_marks=data.get('total_marks', exam.total_marks),
            passing_marks=data.get('passing_marks', exam.passing_marks),
            question_paper_code=data.get('question_paper_code'),
            special_instructions=data.get('special_instructions'),
            materials_allowed=data.get('materials_allowed'),
            materials_provided=data.get('materials_provided')
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'message': 'Exam schedule created successfully',
            'schedule': schedule.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exams_bp.route('/<int:exam_id>/results', methods=['GET'])
@jwt_required()
def get_exam_results(exam_id):
    """Get exam results"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        exam = Exam.query.get(exam_id)
        if not exam or exam.school_id != user.school_id:
            return jsonify({'error': 'Exam not found'}), 404
        
        query = ExamResult.query.filter_by(exam_id=exam_id)
        
        # Filter by user role
        if user.role == 'student':
            student = Student.query.filter_by(user_id=user.id).first()
            if student:
                query = query.filter_by(student_id=student.id)
            if not exam.results_published:
                return jsonify({'error': 'Results not yet published'}), 403
        
        elif user.role == 'teacher':
            staff = Staff.query.filter_by(user_id=user.id).first()
            if staff and staff.position != 'Administrator':
                # Teachers see results for subjects they teach
                taught_subjects = [s.id for s in Subject.query.filter_by(teacher_id=staff.id).all()]
                query = query.filter(ExamResult.subject_id.in_(taught_subjects))
        
        results = query.all()
        
        return jsonify({
            'results': [result.to_dict() for result in results],
            'total': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exams_bp.route('/<int:exam_id>/results', methods=['POST'])
@jwt_required()
def create_exam_result():
    """Create or update exam result"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['exam_id', 'student_id', 'subject_id', 'class_id', 'marks_obtained', 'total_marks']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if result already exists
        existing_result = ExamResult.query.filter_by(
            exam_id=data['exam_id'],
            student_id=data['student_id'],
            subject_id=data['subject_id']
        ).first()
        
        if existing_result:
            # Update existing result
            result = existing_result
            result.marks_obtained = data['marks_obtained']
            result.total_marks = data['total_marks']
        else:
            # Create new result
            result = ExamResult(
                exam_id=data['exam_id'],
                student_id=data['student_id'],
                subject_id=data['subject_id'],
                class_id=data['class_id'],
                marks_obtained=data['marks_obtained'],
                total_marks=data['total_marks'],
                created_by_id=user.id
            )
            db.session.add(result)
        
        # Calculate percentage and grade
        result.percentage = (result.marks_obtained / result.total_marks) * 100
        result.calculate_grade()
        
        # Add additional fields
        result.remarks = data.get('remarks')
        result.teacher_comments = data.get('teacher_comments')
        result.updated_by_id = user.id
        result.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Exam result saved successfully',
            'result': result.to_dict()
        }), 201 if not existing_result else 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exams_bp.route('/<int:exam_id>/results/publish', methods=['POST'])
@jwt_required()
def publish_exam_results(exam_id):
    """Publish exam results"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        exam = Exam.query.get(exam_id)
        if not exam or exam.school_id != user.school_id:
            return jsonify({'error': 'Exam not found'}), 404
        
        # Mark exam results as published
        exam.results_published = True
        exam.updated_at = datetime.utcnow()
        
        # Update all results for this exam
        results = ExamResult.query.filter_by(exam_id=exam_id).all()
        for result in results:
            result.is_published = True
            result.published_at = datetime.utcnow()
        
        db.session.commit()
        
        # Send notifications to students and parents
        from app.services.notification_service import notification_service
        
        for result in results:
            # Get student's results for this exam
            student_results = ExamResult.query.filter_by(
                exam_id=exam_id, student_id=result.student_id
            ).all()
            
            subject_results = []
            for sr in student_results:
                subject_results.append({
                    'subject': sr.subject.name,
                    'marks': sr.marks_obtained,
                    'total_marks': sr.total_marks,
                    'grade': sr.grade
                })
            
            # Send notification
            notification_service.send_exam_result_notification(
                result.student_id, exam.name, subject_results
            )
        
        return jsonify({
            'message': f'Results published for {len(results)} students',
            'exam': exam.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@exams_bp.route('/<int:exam_id>/analytics', methods=['GET'])
@jwt_required()
def get_exam_analytics(exam_id):
    """Get exam performance analytics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        exam = Exam.query.get(exam_id)
        if not exam or exam.school_id != user.school_id:
            return jsonify({'error': 'Exam not found'}), 404
        
        results = ExamResult.query.filter_by(exam_id=exam_id).all()
        
        if not results:
            return jsonify({'analytics': {'message': 'No results available'}})
        
        # Overall statistics
        total_students = len(set([r.student_id for r in results]))
        total_subjects = len(set([r.subject_id for r in results]))
        
        all_percentages = [r.percentage for r in results if r.percentage is not None]
        
        overall_stats = {
            'total_students': total_students,
            'total_subjects': total_subjects,
            'average_score': sum(all_percentages) / len(all_percentages) if all_percentages else 0,
            'highest_score': max(all_percentages) if all_percentages else 0,
            'lowest_score': min(all_percentages) if all_percentages else 0,
            'pass_rate': len([p for p in all_percentages if p >= exam.passing_marks]) / len(all_percentages) * 100 if all_percentages else 0
        }
        
        # Grade distribution
        grade_distribution = {}
        for result in results:
            if result.grade:
                grade_distribution[result.grade] = grade_distribution.get(result.grade, 0) + 1
        
        # Subject-wise performance
        subject_performance = {}
        for result in results:
            subject_name = result.subject.name
            if subject_name not in subject_performance:
                subject_performance[subject_name] = []
            subject_performance[subject_name].append(result.percentage or 0)
        
        # Calculate subject averages
        subject_averages = {}
        for subject, scores in subject_performance.items():
            subject_averages[subject] = {
                'average': sum(scores) / len(scores),
                'highest': max(scores),
                'lowest': min(scores),
                'students_count': len(scores)
            }
        
        # Class-wise performance
        class_performance = {}
        for result in results:
            class_name = result.class_obj.name
            if class_name not in class_performance:
                class_performance[class_name] = []
            class_performance[class_name].append(result.percentage or 0)
        
        class_averages = {}
        for class_name, scores in class_performance.items():
            class_averages[class_name] = {
                'average': sum(scores) / len(scores),
                'students_count': len(set([r.student_id for r in results if r.class_obj.name == class_name]))
            }
        
        analytics = {
            'overall_statistics': overall_stats,
            'grade_distribution': grade_distribution,
            'subject_performance': subject_averages,
            'class_performance': class_averages,
            'exam_info': exam.to_dict()
        }
        
        return jsonify({'analytics': analytics})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500