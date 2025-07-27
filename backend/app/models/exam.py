from app import db
from datetime import datetime
import uuid

class Exam(db.Model):
    __tablename__ = 'exams'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # School relationship for multi-tenancy
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    
    # Basic Information
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    exam_type = db.Column(db.String(50), nullable=False)  # mid-term, final, cat, quiz, etc.
    academic_year = db.Column(db.String(10), nullable=False)
    term = db.Column(db.String(20), nullable=False)
    
    # Timing
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    registration_deadline = db.Column(db.Date)
    results_release_date = db.Column(db.Date)
    
    # Configuration
    total_marks = db.Column(db.Integer, default=100)
    passing_marks = db.Column(db.Integer, default=50)
    grading_scale = db.Column(db.String(20), default='A-F')  # A-F, 1-7, percentage
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, ongoing, completed, cancelled
    is_published = db.Column(db.Boolean, default=False)
    results_published = db.Column(db.Boolean, default=False)
    
    # Instructions and Rules
    instructions = db.Column(db.Text)
    rules = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit trail
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    exam_schedules = db.relationship('ExamSchedule', backref='exam', lazy='dynamic', cascade='all, delete-orphan')
    exam_results = db.relationship('ExamResult', backref='exam', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_subjects(self):
        """Get all subjects for this exam"""
        return [schedule.subject for schedule in self.exam_schedules.all()]
    
    def get_classes(self):
        """Get all classes taking this exam"""
        classes = set()
        for schedule in self.exam_schedules.all():
            classes.add(schedule.class_obj)
        return list(classes)
    
    def get_statistics(self):
        """Get exam statistics"""
        total_students = 0
        total_subjects = self.exam_schedules.count()
        completed_subjects = 0
        
        for schedule in self.exam_schedules.all():
            total_students += schedule.get_registered_students_count()
            if schedule.status == 'completed':
                completed_subjects += 1
        
        return {
            'total_subjects': total_subjects,
            'completed_subjects': completed_subjects,
            'total_students': total_students,
            'completion_percentage': round((completed_subjects / total_subjects) * 100, 2) if total_subjects > 0 else 0
        }
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'school_id': self.school_id,
            'name': self.name,
            'description': self.description,
            'exam_type': self.exam_type,
            'academic_year': self.academic_year,
            'term': self.term,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            'results_release_date': self.results_release_date.isoformat() if self.results_release_date else None,
            'total_marks': self.total_marks,
            'passing_marks': self.passing_marks,
            'grading_scale': self.grading_scale,
            'status': self.status,
            'is_published': self.is_published,
            'results_published': self.results_published,
            'instructions': self.instructions,
            'rules': self.rules,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'statistics': self.get_statistics()
        }
    
    def __repr__(self):
        return f'<Exam {self.name} ({self.academic_year}/{self.term})>'


class ExamSchedule(db.Model):
    __tablename__ = 'exam_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)  # Invigilator
    
    # Schedule Details
    exam_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    
    # Venue and Logistics
    venue = db.Column(db.String(100))
    room_number = db.Column(db.String(20))
    seating_arrangement = db.Column(db.String(50))  # alphabetical, roll_number, random
    max_students = db.Column(db.Integer)
    
    # Exam Configuration
    total_marks = db.Column(db.Integer, default=100)
    passing_marks = db.Column(db.Integer, default=50)
    question_paper_code = db.Column(db.String(20))
    
    # Status
    status = db.Column(db.String(20), default='scheduled')  # scheduled, ongoing, completed, cancelled
    
    # Special Instructions
    special_instructions = db.Column(db.Text)
    materials_allowed = db.Column(db.Text)
    materials_provided = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = db.relationship('Subject', backref='exam_schedules')
    class_obj = db.relationship('Class', backref='exam_schedules')
    teacher = db.relationship('Staff', backref='exam_schedules')
    
    def get_registered_students(self):
        """Get students registered for this exam"""
        return self.class_obj.students.filter_by(is_active=True).all() if self.class_obj else []
    
    def get_registered_students_count(self):
        """Get count of students registered for this exam"""
        return len(self.get_registered_students())
    
    def get_exam_results(self):
        """Get results for this exam schedule"""
        return ExamResult.query.filter_by(
            exam_id=self.exam_id,
            subject_id=self.subject_id,
            class_id=self.class_id
        ).all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'exam_id': self.exam_id,
            'subject_id': self.subject_id,
            'class_id': self.class_id,
            'teacher_id': self.teacher_id,
            'subject_name': self.subject.name if self.subject else None,
            'class_name': self.class_obj.name if self.class_obj else None,
            'teacher_name': self.teacher.user.get_full_name() if self.teacher and self.teacher.user else None,
            'exam_date': self.exam_date.isoformat() if self.exam_date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'venue': self.venue,
            'room_number': self.room_number,
            'seating_arrangement': self.seating_arrangement,
            'max_students': self.max_students,
            'total_marks': self.total_marks,
            'passing_marks': self.passing_marks,
            'question_paper_code': self.question_paper_code,
            'status': self.status,
            'special_instructions': self.special_instructions,
            'materials_allowed': self.materials_allowed,
            'materials_provided': self.materials_provided,
            'registered_students_count': self.get_registered_students_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ExamSchedule {self.exam.name} - {self.subject.name if self.subject else "Unknown"} ({self.exam_date})>'


class ExamResult(db.Model):
    __tablename__ = 'exam_results'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    
    # Scores
    marks_obtained = db.Column(db.Float, nullable=False)
    total_marks = db.Column(db.Integer, nullable=False, default=100)
    percentage = db.Column(db.Float)
    grade = db.Column(db.String(5))
    points = db.Column(db.Float)  # For GPA calculation
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, published, disputed
    is_published = db.Column(db.Boolean, default=False)
    
    # Additional Information
    remarks = db.Column(db.Text)
    teacher_comments = db.Column(db.Text)
    position_in_class = db.Column(db.Integer)
    position_in_subject = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Audit trail
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    student = db.relationship('Student', backref='exam_results')
    subject = db.relationship('Subject', backref='exam_results')
    class_obj = db.relationship('Class', backref='exam_results')
    
    def calculate_grade(self):
        """Calculate grade based on percentage"""
        if not self.percentage:
            self.percentage = (self.marks_obtained / self.total_marks) * 100
        
        # Standard Kenyan grading system
        if self.percentage >= 80:
            self.grade = 'A'
            self.points = 12
        elif self.percentage >= 75:
            self.grade = 'A-'
            self.points = 11
        elif self.percentage >= 70:
            self.grade = 'B+'
            self.points = 10
        elif self.percentage >= 65:
            self.grade = 'B'
            self.points = 9
        elif self.percentage >= 60:
            self.grade = 'B-'
            self.points = 8
        elif self.percentage >= 55:
            self.grade = 'C+'
            self.points = 7
        elif self.percentage >= 50:
            self.grade = 'C'
            self.points = 6
        elif self.percentage >= 45:
            self.grade = 'C-'
            self.points = 5
        elif self.percentage >= 40:
            self.grade = 'D+'
            self.points = 4
        elif self.percentage >= 35:
            self.grade = 'D'
            self.points = 3
        elif self.percentage >= 30:
            self.grade = 'D-'
            self.points = 2
        else:
            self.grade = 'E'
            self.points = 1
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'exam_id': self.exam_id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'class_id': self.class_id,
            'exam_name': self.exam.name if self.exam else None,
            'student_name': self.student.full_name if self.student else None,
            'subject_name': self.subject.name if self.subject else None,
            'class_name': self.class_obj.name if self.class_obj else None,
            'marks_obtained': self.marks_obtained,
            'total_marks': self.total_marks,
            'percentage': self.percentage,
            'grade': self.grade,
            'points': self.points,
            'status': self.status,
            'is_published': self.is_published,
            'remarks': self.remarks,
            'teacher_comments': self.teacher_comments,
            'position_in_class': self.position_in_class,
            'position_in_subject': self.position_in_subject,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
    
    def __repr__(self):
        return f'<ExamResult {self.student.full_name if self.student else "Unknown"} - {self.subject.name if self.subject else "Unknown"}: {self.marks_obtained}/{self.total_marks}>'