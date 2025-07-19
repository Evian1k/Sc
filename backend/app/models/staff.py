from app import db
from datetime import datetime

class Staff(db.Model):
    __tablename__ = 'staff'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    staff_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    position = db.Column(db.String(100), nullable=False)  # Teacher, Principal, Admin, etc.
    department = db.Column(db.String(100))
    salary = db.Column(db.Decimal(10, 2))
    hire_date = db.Column(db.Date, default=datetime.utcnow().date)
    qualification = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'staff_id': self.staff_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'phone': self.phone,
            'address': self.address,
            'position': self.position,
            'department': self.department,
            'salary': float(self.salary) if self.salary else None,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'qualification': self.qualification,
            'emergency_contact': self.emergency_contact,
            'emergency_phone': self.emergency_phone,
            'is_active': self.is_active,
            'email': self.user.email if self.user else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }