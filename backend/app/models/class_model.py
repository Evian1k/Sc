from app import db
from datetime import datetime
import uuid

class Class(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # School relationship for multi-tenancy
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    
    # Basic Information
    name = db.Column(db.String(100), nullable=False)  # e.g., "Grade 10A", "Class 5B"
    section = db.Column(db.String(10), nullable=False)  # A, B, C, etc.
    grade_level = db.Column(db.Integer, nullable=False)  # 1-12
    academic_year = db.Column(db.String(20), nullable=False)  # e.g., "2023-2024"
    term = db.Column(db.String(20))  # Current term
    
    # Class Management
    class_teacher_id = db.Column(db.Integer, db.ForeignKey('staff.id'))  # Primary class teacher
    capacity = db.Column(db.Integer, default=30)
    room_number = db.Column(db.String(20))
    
    # Schedule
    schedule = db.Column(db.JSON)  # Class timetable
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit trail
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    students = db.relationship('Student', backref='class_enrolled', lazy='dynamic')
    class_teacher = db.relationship('Staff', backref='taught_classes')
    
    def get_active_students(self):
        """Get active students in this class"""
        return self.students.filter_by(is_active=True).all()
    
    def get_student_count(self):
        """Get count of active students"""
        return self.students.filter_by(is_active=True).count()
    
    def get_subjects(self):
        """Get subjects taught in this class"""
        # This would need to be implemented based on subject-class relationships
        return []
    
    def get_attendance_percentage(self, start_date=None, end_date=None):
        """Calculate average attendance percentage for the class"""
        students = self.get_active_students()
        if not students:
            return 0
        
        total_percentage = 0
        for student in students:
            total_percentage += student.get_attendance_percentage(start_date, end_date)
        
        return round(total_percentage / len(students), 2)
    
    def get_average_grade(self):
        """Calculate average grade for the class"""
        students = self.get_active_students()
        if not students:
            return None
        
        total_grades = 0
        student_count = 0
        
        for student in students:
            grade = student.get_overall_grade()
            if grade is not None:
                total_grades += grade
                student_count += 1
        
        return round(total_grades / student_count, 2) if student_count > 0 else None
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'school_id': self.school_id,
            'name': self.name,
            'section': self.section,
            'grade_level': self.grade_level,
            'academic_year': self.academic_year,
            'term': self.term,
            'class_teacher_id': self.class_teacher_id,
            'class_teacher_name': self.class_teacher.user.get_full_name() if self.class_teacher and self.class_teacher.user else None,
            'capacity': self.capacity,
            'room_number': self.room_number,
            'schedule': self.schedule,
            'is_active': self.is_active,
            'student_count': self.get_student_count(),
            'attendance_percentage': self.get_attendance_percentage(),
            'average_grade': self.get_average_grade(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Class {self.name} ({self.academic_year})>'