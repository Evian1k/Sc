from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Student, Staff, Attendance, Grade, Fee
from datetime import datetime, timedelta
from sqlalchemy import func

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    """Get dashboard analytics for the school"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Basic counts
        total_students = Student.query.filter_by(school_id=user.school_id, is_active=True).count()
        total_staff = Staff.query.filter_by(school_id=user.school_id, is_active=True).count()
        
        # Attendance analytics (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        attendance_records = db.session.query(Attendance).join(Student).filter(
            Student.school_id == user.school_id,
            Attendance.date >= thirty_days_ago.date()
        ).all()
        
        present_count = len([a for a in attendance_records if a.status == 'present'])
        attendance_rate = (present_count / len(attendance_records) * 100) if attendance_records else 0
        
        # Fee analytics
        total_fees_due = db.session.query(func.sum(Fee.amount)).join(Student).filter(
            Student.school_id == user.school_id
        ).scalar() or 0
        
        total_fees_paid = db.session.query(func.sum(Fee.amount_paid)).join(Student).filter(
            Student.school_id == user.school_id
        ).scalar() or 0
        
        # Grade analytics
        recent_grades = db.session.query(Grade).join(Student).filter(
            Student.school_id == user.school_id,
            Grade.created_at >= thirty_days_ago
        ).all()
        
        avg_performance = sum(g.percentage for g in recent_grades if g.percentage) / len(recent_grades) if recent_grades else 0

        analytics = {
            'total_students': total_students,
            'total_staff': total_staff,
            'attendance_rate': round(attendance_rate, 2),
            'total_fees_due': float(total_fees_due),
            'total_fees_paid': float(total_fees_paid),
            'collection_rate': round((total_fees_paid / total_fees_due * 100) if total_fees_due > 0 else 0, 2),
            'average_performance': round(avg_performance, 2),
            'recent_activities': len(attendance_records) + len(recent_grades)
        }

        return jsonify({'analytics': analytics})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/performance', methods=['GET'])
@jwt_required()
def get_performance_analytics():
    """Get detailed performance analytics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get query parameters
        academic_year = request.args.get('academic_year', datetime.now().year)
        term = request.args.get('term', '1')

        # Performance by class
        grades = db.session.query(Grade).join(Student).filter(
            Student.school_id == user.school_id,
            Grade.academic_year == academic_year,
            Grade.term == term
        ).all()

        class_performance = {}
        subject_performance = {}

        for grade in grades:
            # Class performance
            class_name = grade.student.class_enrolled.name if grade.student.class_enrolled else 'Unknown'
            if class_name not in class_performance:
                class_performance[class_name] = []
            if grade.percentage:
                class_performance[class_name].append(grade.percentage)

            # Subject performance
            subject_name = grade.subject.name if grade.subject else 'Unknown'
            if subject_name not in subject_performance:
                subject_performance[subject_name] = []
            if grade.percentage:
                subject_performance[subject_name].append(grade.percentage)

        # Calculate averages
        class_averages = {
            cls: {
                'average': sum(scores) / len(scores),
                'count': len(scores)
            } for cls, scores in class_performance.items() if scores
        }

        subject_averages = {
            subj: {
                'average': sum(scores) / len(scores),
                'highest': max(scores),
                'lowest': min(scores),
                'count': len(scores)
            } for subj, scores in subject_performance.items() if scores
        }

        return jsonify({
            'class_performance': class_averages,
            'subject_performance': subject_averages,
            'total_grades': len(grades)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500