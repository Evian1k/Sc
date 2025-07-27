from app import db
from datetime import datetime
import uuid

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # School relationship for multi-tenancy
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    
    # Student Identification
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    admission_number = db.Column(db.String(20), unique=True)
    national_id = db.Column(db.String(20))
    birth_certificate_number = db.Column(db.String(50))
    passport_number = db.Column(db.String(20))
    
    # Personal Information
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    place_of_birth = db.Column(db.String(100))
    gender = db.Column(db.String(10), nullable=False)
    nationality = db.Column(db.String(50), default='Kenyan')
    religion = db.Column(db.String(50))
    blood_group = db.Column(db.String(5))
    
    # Contact Information
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    
    # Academic Information
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    admission_date = db.Column(db.Date, default=datetime.utcnow().date)
    academic_year = db.Column(db.String(10))
    previous_school = db.Column(db.String(100))
    
    # Legacy parent fields (will be deprecated in favor of ParentStudentRelationship)
    parent_name = db.Column(db.String(100))
    parent_phone = db.Column(db.String(20))
    parent_email = db.Column(db.String(120))
    
    # Emergency Contact Information
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relationship = db.Column(db.String(50))
    emergency_contact_address = db.Column(db.Text)
    
    # Medical Information
    medical_conditions = db.Column(db.Text)
    allergies = db.Column(db.Text)
    medications = db.Column(db.Text)
    doctor_name = db.Column(db.String(100))
    doctor_phone = db.Column(db.String(20))
    hospital_preference = db.Column(db.String(100))
    
    # Financial Information
    fee_structure_id = db.Column(db.Integer, db.ForeignKey('fee_structure.id'))
    scholarship_percentage = db.Column(db.Float, default=0.0)
    discount_percentage = db.Column(db.Float, default=0.0)
    
    # Academic Status
    current_grade_level = db.Column(db.String(20))
    enrollment_status = db.Column(db.String(20), default='active')  # active, graduated, transferred, suspended, expelled
    graduation_date = db.Column(db.Date)
    transfer_date = db.Column(db.Date)
    reason_for_leaving = db.Column(db.Text)
    
    # Additional Information
    special_needs = db.Column(db.Text)
    extracurricular_activities = db.Column(db.JSON)
    profile_picture = db.Column(db.String(255))
    transport_mode = db.Column(db.String(20))  # walking, bus, private, bicycle
    bus_route_id = db.Column(db.Integer, db.ForeignKey('bus_route.id'), nullable=True)
    
    # QR Code for attendance
    qr_code = db.Column(db.String(255))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit trail
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy='dynamic')
    grades = db.relationship('Grade', backref='student', lazy='dynamic')
    fee_records = db.relationship('Fee', backref='student', lazy='dynamic')
    disciplinary_records = db.relationship('DisciplinaryRecord', backref='student', lazy='dynamic')
    library_transactions = db.relationship('LibraryTransaction', backref='student', lazy='dynamic')
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def get_parents(self):
        """Get all parents associated with this student"""
        return [relationship.parent for relationship in self.parent_student_relationships if relationship.is_active]
    
    def get_primary_parent(self):
        """Get the primary parent/guardian"""
        for relationship in self.parent_student_relationships:
            if relationship.is_active and relationship.parent.is_primary_guardian:
                return relationship.parent
        return None
    
    def get_current_age(self):
        """Calculate current age"""
        if self.date_of_birth:
            today = datetime.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def get_attendance_percentage(self, period_start=None, period_end=None):
        """Calculate attendance percentage for a given period"""
        query = self.attendance_records
        if period_start:
            query = query.filter(db.func.date(self.attendance_records.c.date) >= period_start)
        if period_end:
            query = query.filter(db.func.date(self.attendance_records.c.date) <= period_end)
        
        total_days = query.count()
        if total_days == 0:
            return 0
        
        present_days = query.filter_by(status='present').count()
        return round((present_days / total_days) * 100, 2)
    
    def get_overall_grade(self):
        """Calculate overall grade/GPA"""
        grades = self.grades.filter_by(is_active=True).all()
        if not grades:
            return None
        
        total_score = sum(grade.score for grade in grades if grade.score is not None)
        return round(total_score / len(grades), 2)
    
    def get_fee_balance(self):
        """Get current fee balance"""
        total_fees = sum(fee.amount for fee in self.fee_records.filter_by(status='pending').all())
        total_payments = sum(fee.amount_paid for fee in self.fee_records.all())
        return total_fees - total_payments
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'user_id': self.user_id,
            'school_id': self.school_id,
            'student_id': self.student_id,
            'admission_number': self.admission_number,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': self.get_current_age(),
            'place_of_birth': self.place_of_birth,
            'gender': self.gender,
            'nationality': self.nationality,
            'religion': self.religion,
            'blood_group': self.blood_group,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'class_id': self.class_id,
            'class_name': self.class_enrolled.name if self.class_enrolled else None,
            'admission_date': self.admission_date.isoformat() if self.admission_date else None,
            'academic_year': self.academic_year,
            'previous_school': self.previous_school,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'emergency_contact_relationship': self.emergency_contact_relationship,
            'current_grade_level': self.current_grade_level,
            'enrollment_status': self.enrollment_status,
            'graduation_date': self.graduation_date.isoformat() if self.graduation_date else None,
            'scholarship_percentage': self.scholarship_percentage,
            'discount_percentage': self.discount_percentage,
            'extracurricular_activities': self.extracurricular_activities,
            'profile_picture': self.profile_picture,
            'transport_mode': self.transport_mode,
            'qr_code': self.qr_code,
            'is_active': self.is_active,
            'email': self.user.email if self.user else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'attendance_percentage': self.get_attendance_percentage(),
            'overall_grade': self.get_overall_grade(),
            'fee_balance': self.get_fee_balance(),
            'parents_count': len(self.get_parents()) if hasattr(self, 'parent_student_relationships') else 0
        }
        
        if include_sensitive:
            data.update({
                'national_id': self.national_id,
                'birth_certificate_number': self.birth_certificate_number,
                'passport_number': self.passport_number,
                'medical_conditions': self.medical_conditions,
                'allergies': self.allergies,
                'medications': self.medications,
                'doctor_name': self.doctor_name,
                'doctor_phone': self.doctor_phone,
                'hospital_preference': self.hospital_preference,
                'special_needs': self.special_needs,
                'emergency_contact_address': self.emergency_contact_address,
                'transfer_date': self.transfer_date.isoformat() if self.transfer_date else None,
                'reason_for_leaving': self.reason_for_leaving
            })
        
        return data
    
    def __repr__(self):
        return f'<Student {self.student_id}: {self.full_name}>'