from app import db
from datetime import datetime

class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    assessment_type = db.Column(db.String(50), nullable=False)  # exam, quiz, assignment, project
    assessment_name = db.Column(db.String(100), nullable=False)
    marks_obtained = db.Column(db.Decimal(5, 2), nullable=False)
    total_marks = db.Column(db.Decimal(5, 2), nullable=False)
    percentage = db.Column(db.Decimal(5, 2))
    grade_letter = db.Column(db.String(5))  # A+, A, B+, B, C, D, F
    semester = db.Column(db.String(20))
    academic_year = db.Column(db.String(20))
    date_assessed = db.Column(db.Date, default=datetime.utcnow().date)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id])
    
    def calculate_percentage(self):
        if self.total_marks and self.total_marks > 0:
            self.percentage = (self.marks_obtained / self.total_marks) * 100
        return self.percentage
    
    def calculate_grade_letter(self):
        if self.percentage is None:
            self.calculate_percentage()
        
        if self.percentage >= 90:
            self.grade_letter = 'A+'
        elif self.percentage >= 80:
            self.grade_letter = 'A'
        elif self.percentage >= 70:
            self.grade_letter = 'B+'
        elif self.percentage >= 60:
            self.grade_letter = 'B'
        elif self.percentage >= 50:
            self.grade_letter = 'C'
        elif self.percentage >= 40:
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
            'subject_code': self.subject.code if self.subject else None,
            'assessment_type': self.assessment_type,
            'assessment_name': self.assessment_name,
            'marks_obtained': float(self.marks_obtained) if self.marks_obtained else None,
            'total_marks': float(self.total_marks) if self.total_marks else None,
            'percentage': float(self.percentage) if self.percentage else None,
            'grade_letter': self.grade_letter,
            'semester': self.semester,
            'academic_year': self.academic_year,
            'date_assessed': self.date_assessed.isoformat() if self.date_assessed else None,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.username if self.teacher else None,
            'comments': self.comments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }