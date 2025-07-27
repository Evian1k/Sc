from app import db
from datetime import datetime
import uuid

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Basic Information
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(20), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Contact Information
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50), default='Kenya')
    postal_code = db.Column(db.String(10))
    
    # Branding and Customization
    logo_url = db.Column(db.String(255))
    banner_url = db.Column(db.String(255))
    primary_color = db.Column(db.String(7), default='#3B82F6')  # Hex color
    secondary_color = db.Column(db.String(7), default='#10B981')
    website = db.Column(db.String(255))
    
    # Academic Configuration
    academic_year_start = db.Column(db.Date)
    academic_year_end = db.Column(db.Date)
    current_term = db.Column(db.String(20))
    total_terms = db.Column(db.Integer, default=3)
    
    # Subscription and Status
    subscription_type = db.Column(db.String(20), default='free')  # free, basic, premium, enterprise
    subscription_start = db.Column(db.Date)
    subscription_end = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    max_students = db.Column(db.Integer, default=100)
    max_staff = db.Column(db.Integer, default=20)
    
    # Features enabled
    features_enabled = db.Column(db.JSON, default=lambda: {
        'sms_notifications': True,
        'email_notifications': True,
        'biometric_attendance': False,
        'library_management': True,
        'exam_management': True,
        'parent_portal': True,
        'fee_management': True,
        'analytics': True
    })
    
    # Settings
    settings = db.Column(db.JSON, default=lambda: {
        'timezone': 'Africa/Nairobi',
        'date_format': 'DD/MM/YYYY',
        'time_format': '24h',
        'currency': 'KES',
        'language': 'en',
        'auto_backup': True,
        'notification_preferences': {
            'attendance_alerts': True,
            'fee_reminders': True,
            'exam_notifications': True
        }
    })
    
    # Domain and subdomain for multi-tenancy
    domain = db.Column(db.String(100), unique=True)
    subdomain = db.Column(db.String(50), unique=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='school', lazy='dynamic')
    students = db.relationship('Student', backref='school', lazy='dynamic')
    staff = db.relationship('Staff', backref='school', lazy='dynamic')
    classes = db.relationship('Class', backref='school', lazy='dynamic')
    subjects = db.relationship('Subject', backref='school', lazy='dynamic')
    
    def get_current_academic_year(self):
        """Get current academic year string"""
        if self.academic_year_start and self.academic_year_end:
            return f"{self.academic_year_start.year}/{self.academic_year_end.year}"
        return None
    
    def is_feature_enabled(self, feature):
        """Check if a specific feature is enabled"""
        return self.features_enabled.get(feature, False)
    
    def get_setting(self, key, default=None):
        """Get a specific setting value"""
        return self.settings.get(key, default)
    
    def update_setting(self, key, value):
        """Update a specific setting"""
        if self.settings is None:
            self.settings = {}
        self.settings[key] = value
        db.session.commit()
    
    def get_stats(self):
        """Get basic school statistics"""
        return {
            'total_students': self.students.filter_by(is_active=True).count(),
            'total_staff': self.staff.filter_by(is_active=True).count(),
            'total_classes': self.classes.filter_by(is_active=True).count(),
            'total_subjects': self.subjects.count()
        }
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'short_name': self.short_name,
            'code': self.code,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'logo_url': self.logo_url,
            'banner_url': self.banner_url,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'website': self.website,
            'academic_year_start': self.academic_year_start.isoformat() if self.academic_year_start else None,
            'academic_year_end': self.academic_year_end.isoformat() if self.academic_year_end else None,
            'current_academic_year': self.get_current_academic_year(),
            'current_term': self.current_term,
            'total_terms': self.total_terms,
            'subscription_type': self.subscription_type,
            'subscription_start': self.subscription_start.isoformat() if self.subscription_start else None,
            'subscription_end': self.subscription_end.isoformat() if self.subscription_end else None,
            'is_active': self.is_active,
            'max_students': self.max_students,
            'max_staff': self.max_staff,
            'features_enabled': self.features_enabled,
            'settings': self.settings,
            'domain': self.domain,
            'subdomain': self.subdomain,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'stats': self.get_stats()
        }
    
    def __repr__(self):
        return f'<School {self.name} ({self.code})>'