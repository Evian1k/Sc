from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.class_model import Class
from datetime import datetime, date, time
from sqlalchemy import func

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/', methods=['GET'])
@jwt_required()
def get_attendance():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        student_id = request.args.get('student_id', type=int)
        class_id = request.args.get('class_id', type=int)
        date_str = request.args.get('date')
        status = request.args.get('status')
        
        query = Attendance.query.join(Student)
        
        if student_id:
            query = query.filter(Attendance.student_id == student_id)
        
        if class_id:
            query = query.filter(Student.class_id == class_id)
        
        if date_str:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(Attendance.date == attendance_date)
        
        if status:
            query = query.filter(Attendance.status == status)
        
        attendance_records = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'attendance': [record.to_dict() for record in attendance_records.items],
            'total': attendance_records.total,
            'pages': attendance_records.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/check-in', methods=['POST'])
@jwt_required()
def check_in():
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        attendance_date = data.get('date', date.today().isoformat())
        check_in_time = data.get('check_in_time', datetime.now().time().isoformat())
        status = data.get('status', 'present')
        notes = data.get('notes', '')
        
        user_id = get_jwt_identity()
        
        # Parse date and time
        attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        check_in_time = datetime.strptime(check_in_time, '%H:%M:%S').time()
        
        # Check if attendance already exists for this student on this date
        existing_attendance = Attendance.query.filter_by(
            student_id=student_id,
            date=attendance_date
        ).first()
        
        if existing_attendance:
            # Update existing record
            existing_attendance.status = status
            existing_attendance.check_in_time = check_in_time
            existing_attendance.notes = notes
            existing_attendance.marked_by = user_id
            record = existing_attendance
        else:
            # Create new attendance record
            record = Attendance(
                student_id=student_id,
                date=attendance_date,
                status=status,
                check_in_time=check_in_time,
                notes=notes,
                marked_by=user_id
            )
            db.session.add(record)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Check-in recorded successfully',
            'attendance': record.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/check-out', methods=['POST'])
@jwt_required()
def check_out():
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        attendance_date = data.get('date', date.today().isoformat())
        check_out_time = data.get('check_out_time', datetime.now().time().isoformat())
        
        user_id = get_jwt_identity()
        
        # Parse date and time
        attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        check_out_time = datetime.strptime(check_out_time, '%H:%M:%S').time()
        
        # Find existing attendance record
        record = Attendance.query.filter_by(
            student_id=student_id,
            date=attendance_date
        ).first()
        
        if not record:
            return jsonify({'error': 'No check-in record found for this date'}), 404
        
        record.check_out_time = check_out_time
        record.marked_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Check-out recorded successfully',
            'attendance': record.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/bulk-mark', methods=['POST'])
@jwt_required()
def bulk_mark_attendance():
    try:
        data = request.get_json()
        attendance_date = data.get('date', date.today().isoformat())
        class_id = data.get('class_id')
        attendance_records = data.get('attendance', [])
        
        user_id = get_jwt_identity()
        attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        
        if not class_id and not attendance_records:
            return jsonify({'error': 'Either class_id or attendance records are required'}), 400
        
        processed_records = []
        
        if class_id:
            # Mark attendance for entire class
            students = Student.query.filter_by(class_id=class_id, is_active=True).all()
            
            for student in students:
                # Find student's attendance record in the provided data
                student_attendance = next(
                    (record for record in attendance_records if record.get('student_id') == student.id),
                    {'status': 'present'}
                )
                
                existing_record = Attendance.query.filter_by(
                    student_id=student.id,
                    date=attendance_date
                ).first()
                
                if existing_record:
                    existing_record.status = student_attendance.get('status', 'present')
                    existing_record.notes = student_attendance.get('notes', '')
                    existing_record.marked_by = user_id
                    record = existing_record
                else:
                    record = Attendance(
                        student_id=student.id,
                        date=attendance_date,
                        status=student_attendance.get('status', 'present'),
                        notes=student_attendance.get('notes', ''),
                        marked_by=user_id
                    )
                    db.session.add(record)
                
                processed_records.append(record.to_dict())
        
        else:
            # Mark attendance for individual records
            for attendance_data in attendance_records:
                student_id = attendance_data.get('student_id')
                status = attendance_data.get('status', 'present')
                notes = attendance_data.get('notes', '')
                
                existing_record = Attendance.query.filter_by(
                    student_id=student_id,
                    date=attendance_date
                ).first()
                
                if existing_record:
                    existing_record.status = status
                    existing_record.notes = notes
                    existing_record.marked_by = user_id
                    record = existing_record
                else:
                    record = Attendance(
                        student_id=student_id,
                        date=attendance_date,
                        status=status,
                        notes=notes,
                        marked_by=user_id
                    )
                    db.session.add(record)
                
                processed_records.append(record.to_dict())
        
        db.session.commit()
        
        return jsonify({
            'message': f'Attendance marked for {len(processed_records)} students',
            'attendance': processed_records
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/<int:attendance_id>', methods=['PUT'])
@jwt_required()
def update_attendance(attendance_id):
    try:
        record = Attendance.query.get_or_404(attendance_id)
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Update fields
        if 'status' in data:
            record.status = data['status']
        if 'notes' in data:
            record.notes = data['notes']
        if 'check_in_time' in data:
            record.check_in_time = datetime.strptime(data['check_in_time'], '%H:%M:%S').time()
        if 'check_out_time' in data:
            record.check_out_time = datetime.strptime(data['check_out_time'], '%H:%M:%S').time()
        
        record.marked_by = user_id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Attendance updated successfully',
            'attendance': record.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/report', methods=['GET'])
@jwt_required()
def attendance_report():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        class_id = request.args.get('class_id', type=int)
        student_id = request.args.get('student_id', type=int)
        
        if not start_date or not end_date:
            return jsonify({'error': 'Start date and end date are required'}), 400
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        query = db.session.query(
            Student.id,
            Student.first_name,
            Student.last_name,
            Student.student_id,
            func.count(Attendance.id).label('total_days'),
            func.sum(func.case([(Attendance.status == 'present', 1)], else_=0)).label('present_days'),
            func.sum(func.case([(Attendance.status == 'absent', 1)], else_=0)).label('absent_days'),
            func.sum(func.case([(Attendance.status == 'late', 1)], else_=0)).label('late_days')
        ).join(
            Attendance, Student.id == Attendance.student_id
        ).filter(
            Attendance.date.between(start_date, end_date)
        )
        
        if class_id:
            query = query.filter(Student.class_id == class_id)
        
        if student_id:
            query = query.filter(Student.id == student_id)
        
        results = query.group_by(Student.id).all()
        
        report_data = []
        for result in results:
            attendance_percentage = (result.present_days / result.total_days * 100) if result.total_days > 0 else 0
            
            report_data.append({
                'student_id': result.id,
                'student_name': f"{result.first_name} {result.last_name}",
                'student_number': result.student_id,
                'total_days': result.total_days,
                'present_days': result.present_days,
                'absent_days': result.absent_days,
                'late_days': result.late_days,
                'attendance_percentage': round(attendance_percentage, 2)
            })
        
        return jsonify({
            'report': report_data,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500