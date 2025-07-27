from app import db
from datetime import datetime
import uuid

class FeeStructure(db.Model):
    __tablename__ = 'fee_structure'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # School relationship for multi-tenancy
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    
    # Basic Information
    name = db.Column(db.String(100), nullable=False)  # e.g., "Grade 10 Annual Fees"
    description = db.Column(db.Text)
    fee_type = db.Column(db.String(50), nullable=False)  # tuition, library, lab, transport, exam, etc.
    
    # Applicability
    grade_levels = db.Column(db.JSON)  # List of grade levels this applies to
    class_ids = db.Column(db.JSON)  # Specific classes if not grade-level based
    academic_year = db.Column(db.String(10), nullable=False)
    term = db.Column(db.String(20))  # If term-specific
    
    # Amount Structure
    base_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(5), default='KES')
    
    # Payment Schedule
    payment_frequency = db.Column(db.String(20), default='annual')  # annual, termly, monthly, weekly
    total_installments = db.Column(db.Integer, default=1)
    installment_amount = db.Column(db.Float)
    
    # Due Dates
    due_date = db.Column(db.Date)
    late_fee_amount = db.Column(db.Float, default=0.0)
    late_fee_type = db.Column(db.String(20), default='fixed')  # fixed, percentage, daily
    grace_period_days = db.Column(db.Integer, default=0)
    
    # Discounts and Scholarships
    discount_eligible = db.Column(db.Boolean, default=True)
    scholarship_eligible = db.Column(db.Boolean, default=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_mandatory = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit trail
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    students = db.relationship('Student', backref='fee_structure')
    
    def calculate_amount_for_student(self, student):
        """Calculate fee amount for a specific student considering discounts"""
        amount = self.base_amount
        
        # Apply scholarship discount
        if student.scholarship_percentage > 0 and self.scholarship_eligible:
            amount = amount * (1 - student.scholarship_percentage / 100)
        
        # Apply other discounts
        if student.discount_percentage > 0 and self.discount_eligible:
            amount = amount * (1 - student.discount_percentage / 100)
        
        return round(amount, 2)
    
    def is_applicable_to_student(self, student):
        """Check if this fee structure applies to a student"""
        # Check grade level
        if self.grade_levels and student.current_grade_level not in self.grade_levels:
            return False
        
        # Check specific classes
        if self.class_ids and student.class_id not in self.class_ids:
            return False
        
        # Check academic year
        if student.academic_year != self.academic_year:
            return False
        
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'school_id': self.school_id,
            'name': self.name,
            'description': self.description,
            'fee_type': self.fee_type,
            'grade_levels': self.grade_levels,
            'class_ids': self.class_ids,
            'academic_year': self.academic_year,
            'term': self.term,
            'base_amount': self.base_amount,
            'currency': self.currency,
            'payment_frequency': self.payment_frequency,
            'total_installments': self.total_installments,
            'installment_amount': self.installment_amount,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'late_fee_amount': self.late_fee_amount,
            'late_fee_type': self.late_fee_type,
            'grace_period_days': self.grace_period_days,
            'discount_eligible': self.discount_eligible,
            'scholarship_eligible': self.scholarship_eligible,
            'is_active': self.is_active,
            'is_mandatory': self.is_mandatory,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<FeeStructure {self.name} - {self.base_amount} {self.currency}>'


class Timetable(db.Model):
    __tablename__ = 'timetables'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # School relationship for multi-tenancy
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    
    # Basic Information
    name = db.Column(db.String(100), nullable=False)  # e.g., "Grade 10A - Term 1 Timetable"
    description = db.Column(db.Text)
    
    # Scope
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('staff.id'))  # For teacher's personal timetable
    
    # Academic Period
    academic_year = db.Column(db.String(10), nullable=False)
    term = db.Column(db.String(20), nullable=False)
    
    # Validity Period
    effective_from = db.Column(db.Date, nullable=False)
    effective_to = db.Column(db.Date)
    
    # Timetable Data
    schedule = db.Column(db.JSON, nullable=False)  # Complex schedule data structure
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_published = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Audit trail
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    class_obj = db.relationship('Class', backref='timetables')
    teacher = db.relationship('Staff', backref='timetables')
    
    def get_schedule_for_day(self, day_of_week):
        """Get schedule for a specific day (0=Monday, 6=Sunday)"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_name = days[day_of_week]
        return self.schedule.get(day_name, [])
    
    def get_current_period(self):
        """Get current period based on current time"""
        from datetime import datetime, time
        
        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()  # 0=Monday
        
        day_schedule = self.get_schedule_for_day(current_day)
        
        for period in day_schedule:
            start_time = datetime.strptime(period['start_time'], '%H:%M').time()
            end_time = datetime.strptime(period['end_time'], '%H:%M').time()
            
            if start_time <= current_time <= end_time:
                return period
        
        return None
    
    def get_next_period(self):
        """Get next upcoming period"""
        from datetime import datetime
        
        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()
        
        day_schedule = self.get_schedule_for_day(current_day)
        
        for period in day_schedule:
            start_time = datetime.strptime(period['start_time'], '%H:%M').time()
            
            if current_time < start_time:
                return period
        
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'school_id': self.school_id,
            'name': self.name,
            'description': self.description,
            'class_id': self.class_id,
            'class_name': self.class_obj.name if self.class_obj else None,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.user.get_full_name() if self.teacher and self.teacher.user else None,
            'academic_year': self.academic_year,
            'term': self.term,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'effective_to': self.effective_to.isoformat() if self.effective_to else None,
            'schedule': self.schedule,
            'is_active': self.is_active,
            'is_published': self.is_published,
            'current_period': self.get_current_period(),
            'next_period': self.get_next_period(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
    
    def __repr__(self):
        return f'<Timetable {self.name} ({self.academic_year}/{self.term})>'


class BusRoute(db.Model):
    __tablename__ = 'bus_route'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # School relationship for multi-tenancy
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    
    # Route Information
    route_name = db.Column(db.String(100), nullable=False)
    route_code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Vehicle Information
    bus_number = db.Column(db.String(20))
    vehicle_registration = db.Column(db.String(20))
    driver_name = db.Column(db.String(100))
    driver_phone = db.Column(db.String(20))
    conductor_name = db.Column(db.String(100))
    conductor_phone = db.Column(db.String(20))
    
    # Route Details
    starting_point = db.Column(db.String(200))
    ending_point = db.Column(db.String(200))
    total_distance = db.Column(db.Float)  # in kilometers
    estimated_duration = db.Column(db.Integer)  # in minutes
    stops = db.Column(db.JSON)  # List of stops with times
    
    # Schedule
    pickup_start_time = db.Column(db.Time)
    pickup_end_time = db.Column(db.Time)
    dropoff_start_time = db.Column(db.Time)
    dropoff_end_time = db.Column(db.Time)
    
    # Capacity and Pricing
    capacity = db.Column(db.Integer, default=30)
    monthly_fee = db.Column(db.Float, default=0.0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='bus_route')
    
    def get_current_occupancy(self):
        """Get current number of students using this route"""
        return len([s for s in self.students if s.is_active])
    
    def get_available_seats(self):
        """Get number of available seats"""
        return self.capacity - self.get_current_occupancy()
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'school_id': self.school_id,
            'route_name': self.route_name,
            'route_code': self.route_code,
            'description': self.description,
            'bus_number': self.bus_number,
            'vehicle_registration': self.vehicle_registration,
            'driver_name': self.driver_name,
            'driver_phone': self.driver_phone,
            'conductor_name': self.conductor_name,
            'conductor_phone': self.conductor_phone,
            'starting_point': self.starting_point,
            'ending_point': self.ending_point,
            'total_distance': self.total_distance,
            'estimated_duration': self.estimated_duration,
            'stops': self.stops,
            'pickup_start_time': self.pickup_start_time.strftime('%H:%M') if self.pickup_start_time else None,
            'pickup_end_time': self.pickup_end_time.strftime('%H:%M') if self.pickup_end_time else None,
            'dropoff_start_time': self.dropoff_start_time.strftime('%H:%M') if self.dropoff_start_time else None,
            'dropoff_end_time': self.dropoff_end_time.strftime('%H:%M') if self.dropoff_end_time else None,
            'capacity': self.capacity,
            'monthly_fee': self.monthly_fee,
            'current_occupancy': self.get_current_occupancy(),
            'available_seats': self.get_available_seats(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<BusRoute {self.route_name} ({self.route_code})>'