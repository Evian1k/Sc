from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Enhanced role system: admin, teacher, student, parent, accountant, superadmin
    role = db.Column(db.String(20), nullable=False, default='student')
    
    # Additional user information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20))
    profile_picture = db.Column(db.String(255))
    
    # Status and security
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    
    # Multi-tenancy support
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Two-factor authentication
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))
    
    # Password reset
    password_reset_token = db.Column(db.String(100))
    password_reset_expires = db.Column(db.DateTime)
    
    # Relationships
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    staff = db.relationship('Staff', backref='user', uselist=False, cascade='all, delete-orphan')
    parent = db.relationship('Parent', backref='user', uselist=False, cascade='all, delete-orphan')
    
    # Audit trail
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Self-referential relationships for audit
    created_by = db.relationship('User', remote_side=[id], foreign_keys=[created_by_id])
    updated_by = db.relationship('User', remote_side=[id], foreign_keys=[updated_by_id])
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self):
        return self.role in ['admin', 'superadmin']
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_student(self):
        return self.role == 'student'
    
    def is_parent(self):
        return self.role == 'parent'
    
    def is_accountant(self):
        return self.role == 'accountant'
    
    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        permissions = {
            'superadmin': ['*'],  # All permissions
            'admin': [
                'manage_users', 'manage_students', 'manage_staff', 'manage_classes',
                'manage_subjects', 'view_all_attendance', 'manage_grades', 'manage_fees',
                'view_reports', 'manage_school_settings', 'manage_timetables',
                'manage_exams', 'manage_library', 'manage_events', 'view_analytics'
            ],
            'teacher': [
                'view_students', 'mark_attendance', 'manage_grades', 'view_classes',
                'view_subjects', 'send_messages', 'view_timetables', 'manage_assignments'
            ],
            'student': [
                'view_own_attendance', 'view_own_grades', 'view_own_fees',
                'view_timetables', 'view_assignments', 'submit_assignments'
            ],
            'parent': [
                'view_child_attendance', 'view_child_grades', 'view_child_fees',
                'receive_notifications', 'communicate_teachers', 'view_child_timetable'
            ],
            'accountant': [
                'manage_fees', 'view_payments', 'generate_financial_reports',
                'manage_expenses', 'view_fee_analytics'
            ]
        }
        
        user_permissions = permissions.get(self.role, [])
        return '*' in user_permissions or permission in user_permissions
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'phone_number': self.phone_number,
            'profile_picture': self.profile_picture,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'email_verified': self.email_verified,
            'phone_verified': self.phone_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'school_id': self.school_id,
            'two_factor_enabled': self.two_factor_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data.update({
                'failed_login_attempts': self.failed_login_attempts,
                'account_locked_until': self.account_locked_until.isoformat() if self.account_locked_until else None
            })
        
        return data
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'