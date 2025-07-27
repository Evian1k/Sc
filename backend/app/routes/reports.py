from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Student, Class, Exam
from app.services.report_service import report_service
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/student/<int:student_id>/report-card', methods=['POST'])
@jwt_required()
def generate_student_report_card(student_id):
    """Generate student report card"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        student = Student.query.get(student_id)
        if not student or student.school_id != user.school_id:
            return jsonify({'error': 'Student not found'}), 404
        
        # Check permissions
        if user.role == 'student' and student.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        elif user.role == 'parent':
            # Check if parent is linked to this student
            from app.models import Parent, ParentStudentRelationship
            parent = Parent.query.filter_by(user_id=user.id).first()
            if not parent:
                return jsonify({'error': 'Parent profile not found'}), 404
            
            relationship = ParentStudentRelationship.query.filter_by(
                parent_id=parent.id, student_id=student_id, is_active=True
            ).first()
            if not relationship or not relationship.can_view_grades:
                return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        academic_year = data.get('academic_year')
        term = data.get('term')
        
        if not academic_year or not term:
            return jsonify({'error': 'Academic year and term are required'}), 400
        
        result = report_service.generate_student_report_card(
            student_id, academic_year, term
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/student/<int:student_id>/fee-statement', methods=['POST'])
@jwt_required()
def generate_fee_statement(student_id):
    """Generate student fee statement"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        student = Student.query.get(student_id)
        if not student or student.school_id != user.school_id:
            return jsonify({'error': 'Student not found'}), 404
        
        # Check permissions
        if user.role == 'student' and student.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        elif user.role == 'parent':
            # Check if parent is linked to this student
            from app.models import Parent, ParentStudentRelationship
            parent = Parent.query.filter_by(user_id=user.id).first()
            if not parent:
                return jsonify({'error': 'Parent profile not found'}), 404
            
            relationship = ParentStudentRelationship.query.filter_by(
                parent_id=parent.id, student_id=student_id, is_active=True
            ).first()
            if not relationship or not relationship.can_view_fees:
                return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        academic_year = data.get('academic_year')
        
        if not academic_year:
            return jsonify({'error': 'Academic year is required'}), 400
        
        result = report_service.generate_fee_statement(student_id, academic_year)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/class/<int:class_id>/performance', methods=['POST'])
@jwt_required()
def generate_class_performance_report(class_id):
    """Generate class performance report"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        class_obj = Class.query.get(class_id)
        if not class_obj or class_obj.school_id != user.school_id:
            return jsonify({'error': 'Class not found'}), 404
        
        data = request.get_json()
        exam_id = data.get('exam_id')
        
        if not exam_id:
            return jsonify({'error': 'Exam ID is required'}), 400
        
        exam = Exam.query.get(exam_id)
        if not exam or exam.school_id != user.school_id:
            return jsonify({'error': 'Exam not found'}), 404
        
        result = report_service.generate_class_performance_report(class_id, exam_id)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/attendance/summary', methods=['POST'])
@jwt_required()
def generate_attendance_report():
    """Generate attendance summary report"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Get parameters
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        class_id = data.get('class_id')
        
        if not start_date or not end_date:
            return jsonify({'error': 'Start date and end date are required'}), 400
        
        from app.models import Attendance, Student
        
        # Build query
        query = db.session.query(Attendance).join(Student).filter(
            Student.school_id == user.school_id,
            Attendance.date >= datetime.strptime(start_date, '%Y-%m-%d').date(),
            Attendance.date <= datetime.strptime(end_date, '%Y-%m-%d').date()
        )
        
        if class_id:
            query = query.filter(Student.class_id == class_id)
        
        attendance_records = query.all()
        
        # Calculate statistics
        total_records = len(attendance_records)
        present_records = len([r for r in attendance_records if r.status == 'present'])
        absent_records = len([r for r in attendance_records if r.status == 'absent'])
        late_records = len([r for r in attendance_records if r.status == 'late'])
        
        # Student-wise breakdown
        student_stats = {}
        for record in attendance_records:
            student_id = record.student_id
            if student_id not in student_stats:
                student_stats[student_id] = {
                    'student_name': record.student.full_name,
                    'student_id': record.student.student_id,
                    'class': record.student.class_enrolled.name if record.student.class_enrolled else 'N/A',
                    'present': 0,
                    'absent': 0,
                    'late': 0,
                    'total': 0
                }
            
            student_stats[student_id][record.status] += 1
            student_stats[student_id]['total'] += 1
        
        # Calculate percentages
        for student_id, stats in student_stats.items():
            if stats['total'] > 0:
                stats['attendance_percentage'] = round((stats['present'] / stats['total']) * 100, 2)
            else:
                stats['attendance_percentage'] = 0
        
        report_data = {
            'summary': {
                'total_records': total_records,
                'present_records': present_records,
                'absent_records': absent_records,
                'late_records': late_records,
                'overall_attendance_rate': round((present_records / total_records * 100), 2) if total_records > 0 else 0
            },
            'student_breakdown': list(student_stats.values()),
            'period': f"{start_date} to {end_date}",
            'class_filter': Class.query.get(class_id).name if class_id else 'All Classes'
        }
        
        return jsonify({
            'success': True,
            'report': report_data,
            'generated_at': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/financial/summary', methods=['POST'])
@jwt_required()
def generate_financial_report():
    """Generate financial summary report"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'accountant']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Get parameters
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        academic_year = data.get('academic_year')
        
        from app.models import Fee, Student
        
        # Build query
        query = db.session.query(Fee).join(Student).filter(
            Student.school_id == user.school_id
        )
        
        if start_date and end_date:
            query = query.filter(
                Fee.created_at >= datetime.strptime(start_date, '%Y-%m-%d'),
                Fee.created_at <= datetime.strptime(end_date, '%Y-%m-%d')
            )
        
        if academic_year:
            query = query.filter(Fee.academic_year == academic_year)
        
        fee_records = query.all()
        
        # Calculate totals
        total_fees_due = sum(fee.amount for fee in fee_records)
        total_fees_paid = sum(fee.amount_paid for fee in fee_records)
        total_outstanding = total_fees_due - total_fees_paid
        
        # Collection rate
        collection_rate = (total_fees_paid / total_fees_due * 100) if total_fees_due > 0 else 0
        
        # Fee type breakdown
        fee_types = {}
        for fee in fee_records:
            if fee.fee_type not in fee_types:
                fee_types[fee.fee_type] = {
                    'total_due': 0,
                    'total_paid': 0,
                    'outstanding': 0,
                    'count': 0
                }
            
            fee_types[fee.fee_type]['total_due'] += fee.amount
            fee_types[fee.fee_type]['total_paid'] += fee.amount_paid
            fee_types[fee.fee_type]['outstanding'] += (fee.amount - fee.amount_paid)
            fee_types[fee.fee_type]['count'] += 1
        
        # Payment status breakdown
        paid_fees = len([f for f in fee_records if f.status == 'paid'])
        pending_fees = len([f for f in fee_records if f.status == 'pending'])
        overdue_fees = len([f for f in fee_records if f.status == 'overdue'])
        
        report_data = {
            'summary': {
                'total_fees_due': round(total_fees_due, 2),
                'total_fees_paid': round(total_fees_paid, 2),
                'total_outstanding': round(total_outstanding, 2),
                'collection_rate': round(collection_rate, 2),
                'total_records': len(fee_records)
            },
            'fee_types': fee_types,
            'payment_status': {
                'paid': paid_fees,
                'pending': pending_fees,
                'overdue': overdue_fees
            },
            'period': f"{start_date} to {end_date}" if start_date and end_date else academic_year or 'All time'
        }
        
        return jsonify({
            'success': True,
            'report': report_data,
            'generated_at': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/academic/performance', methods=['POST'])
@jwt_required()
def generate_academic_performance_report():
    """Generate academic performance report"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Get parameters
        academic_year = data.get('academic_year')
        term = data.get('term')
        class_id = data.get('class_id')
        
        if not academic_year or not term:
            return jsonify({'error': 'Academic year and term are required'}), 400
        
        from app.models import ExamResult, Subject
        
        # Build query
        query = db.session.query(ExamResult).join(Student).join(Exam).filter(
            Student.school_id == user.school_id,
            Exam.academic_year == academic_year,
            Exam.term == term
        )
        
        if class_id:
            query = query.filter(ExamResult.class_id == class_id)
        
        results = query.all()
        
        if not results:
            return jsonify({'success': False, 'message': 'No results found for the specified criteria'})
        
        # Overall statistics
        all_percentages = [r.percentage for r in results if r.percentage is not None]
        
        overall_stats = {
            'total_students': len(set([r.student_id for r in results])),
            'total_subjects': len(set([r.subject_id for r in results])),
            'average_score': round(sum(all_percentages) / len(all_percentages), 2) if all_percentages else 0,
            'highest_score': max(all_percentages) if all_percentages else 0,
            'lowest_score': min(all_percentages) if all_percentages else 0,
            'pass_rate': round(len([p for p in all_percentages if p >= 50]) / len(all_percentages) * 100, 2) if all_percentages else 0
        }
        
        # Subject performance
        subject_performance = {}
        for result in results:
            subject_name = result.subject.name
            if subject_name not in subject_performance:
                subject_performance[subject_name] = []
            if result.percentage is not None:
                subject_performance[subject_name].append(result.percentage)
        
        subject_stats = {}
        for subject, scores in subject_performance.items():
            if scores:
                subject_stats[subject] = {
                    'average': round(sum(scores) / len(scores), 2),
                    'highest': max(scores),
                    'lowest': min(scores),
                    'students_count': len(scores),
                    'pass_rate': round(len([s for s in scores if s >= 50]) / len(scores) * 100, 2)
                }
        
        # Grade distribution
        grade_distribution = {}
        for result in results:
            if result.grade:
                grade_distribution[result.grade] = grade_distribution.get(result.grade, 0) + 1
        
        report_data = {
            'overall_statistics': overall_stats,
            'subject_performance': subject_stats,
            'grade_distribution': grade_distribution,
            'academic_year': academic_year,
            'term': term,
            'class_filter': Class.query.get(class_id).name if class_id else 'All Classes'
        }
        
        return jsonify({
            'success': True,
            'report': report_data,
            'generated_at': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/export/students', methods=['POST'])
@jwt_required()
def export_students_data():
    """Export students data"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        format_type = data.get('format', 'json')  # json, csv, excel
        class_id = data.get('class_id')
        
        # Get students
        query = Student.query.filter_by(school_id=user.school_id, is_active=True)
        
        if class_id:
            query = query.filter_by(class_id=class_id)
        
        students = query.all()
        
        if format_type == 'json':
            students_data = [student.to_dict() for student in students]
            return jsonify({
                'success': True,
                'data': students_data,
                'total': len(students_data),
                'exported_at': datetime.utcnow().isoformat()
            })
        
        # For CSV and Excel formats, you would implement the export logic here
        # This is a simplified version returning the data structure
        
        return jsonify({
            'success': True,
            'message': f'{format_type.upper()} export functionality would be implemented here',
            'total_records': len(students)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_report_templates():
    """Get available report templates"""
    try:
        templates = {
            'student_reports': [
                {'id': 'report_card', 'name': 'Student Report Card', 'description': 'Complete academic report with grades and attendance'},
                {'id': 'fee_statement', 'name': 'Fee Statement', 'description': 'Detailed fee breakdown and payment history'},
                {'id': 'attendance_summary', 'name': 'Attendance Summary', 'description': 'Student attendance overview for a period'}
            ],
            'class_reports': [
                {'id': 'class_performance', 'name': 'Class Performance Report', 'description': 'Class-wide academic performance analysis'},
                {'id': 'class_attendance', 'name': 'Class Attendance Report', 'description': 'Attendance statistics for entire class'}
            ],
            'school_reports': [
                {'id': 'financial_summary', 'name': 'Financial Summary', 'description': 'School-wide financial overview and collection rates'},
                {'id': 'academic_overview', 'name': 'Academic Overview', 'description': 'School academic performance across all classes'},
                {'id': 'enrollment_statistics', 'name': 'Enrollment Statistics', 'description': 'Student enrollment trends and demographics'}
            ],
            'administrative_reports': [
                {'id': 'staff_summary', 'name': 'Staff Summary', 'description': 'Staff information and assignments'},
                {'id': 'discipline_report', 'name': 'Discipline Report', 'description': 'Disciplinary incidents and actions taken'}
            ]
        }
        
        return jsonify({'templates': templates})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500