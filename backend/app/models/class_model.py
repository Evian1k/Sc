from app import db
from datetime import datetime

class Class(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Grade 10A", "Class 5B"
    section = db.Column(db.String(10), nullable=False)  # A, B, C, etc.
    grade_level = db.Column(db.Integer, nullable=False)  # 1-12
    academic_year = db.Column(db.String(20), nullable=False)  # e.g., "2023-2024"
    capacity = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='class_enrolled', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'section': self.section,
            'grade_level': self.grade_level,
            'academic_year': self.academic_year,
            'capacity': self.capacity,
            'is_active': self.is_active,
            'student_count': self.students.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }