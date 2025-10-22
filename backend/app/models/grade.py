from app import db
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Numeric

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    exam_type = db.Column(db.String(50), nullable=False)  # midterm, final, quiz, assignment
    marks_obtained = db.Column(Numeric(5, 2), nullable=False)
    total_marks = db.Column(Numeric(5, 2), nullable=False)
    percentage = db.Column(Numeric(5, 2))
    grade_letter = db.Column(db.String(2))  # A+, A, B+, B, C+, C, D, F
    remarks = db.Column(db.Text)
    exam_date = db.Column(db.Date, nullable=False)
    academic_year = db.Column(db.String(10), nullable=False)
    semester = db.Column(db.String(20))
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))  # Teacher who entered the grade
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Grade, self).__init__(**kwargs)
        self.calculate_percentage()
        self.calculate_grade_letter()
    
    def calculate_percentage(self):
        """Calculate percentage based on marks obtained and total marks"""
        if self.marks_obtained is not None and self.total_marks is not None and self.total_marks > 0:
            self.percentage = (self.marks_obtained / self.total_marks) * 100
        return self.percentage
    
    def calculate_grade_letter(self):
        """Calculate grade letter based on percentage"""
        if self.percentage is None:
            return None
            
        percentage = float(self.percentage)
        if percentage >= 97:
            self.grade_letter = 'A+'
        elif percentage >= 93:
            self.grade_letter = 'A'
        elif percentage >= 90:
            self.grade_letter = 'A-'
        elif percentage >= 87:
            self.grade_letter = 'B+'
        elif percentage >= 83:
            self.grade_letter = 'B'
        elif percentage >= 80:
            self.grade_letter = 'B-'
        elif percentage >= 77:
            self.grade_letter = 'C+'
        elif percentage >= 73:
            self.grade_letter = 'C'
        elif percentage >= 70:
            self.grade_letter = 'C-'
        elif percentage >= 67:
            self.grade_letter = 'D+'
        elif percentage >= 65:
            self.grade_letter = 'D'
        else:
            self.grade_letter = 'F'
        
        return self.grade_letter
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'exam_type': self.exam_type,
            'marks_obtained': float(self.marks_obtained),
            'total_marks': float(self.total_marks),
            'percentage': float(self.percentage) if self.percentage else None,
            'grade_letter': self.grade_letter,
            'remarks': self.remarks,
            'exam_date': self.exam_date.isoformat() if self.exam_date else None,
            'academic_year': self.academic_year,
            'semester': self.semester,
            'created_by': self.created_by,
            'teacher_name': self.teacher.full_name if self.teacher else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }