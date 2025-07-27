from app import db
from datetime import datetime
import uuid

class Parent(db.Model):
    __tablename__ = 'parent'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)

    # Personal Info
    title = db.Column(db.String(10))
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    national_id = db.Column(db.String(20))
    passport_number = db.Column(db.String(20))

    # Contact Info
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(20))
    emergency_contact_name = db.Column(db.String(100))
    emergency_relationship = db.Column(db.String(50))

    # Work Info
    occupation = db.Column(db.String(100))
    employer = db.Column(db.String(100))
    work_address = db.Column(db.Text)
    work_phone = db.Column(db.String(20))

    # Preferences
    preferred_communication = db.Column(db.String(20), default='sms')
    notification_preferences = db.Column(db.JSON, default=lambda: {
        'attendance_alerts': True,
        'academic_updates': True,
        'fee_reminders': True,
        'disciplinary_notices': True,
        'event_notifications': True,
        'exam_results': True
    })

    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_primary_guardian = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Helper Methods
    def get_children(self):
        return [rel.student for rel in self.parent_student_relationships]

    def get_notification_preference(self, notif_type):
        return self.notification_preferences.get(notif_type, False)

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'user_id': self.user_id,
            'school_id': self.school_id,
            'title': self.title,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'national_id': self.national_id,
            'passport_number': self.passport_number,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_relationship': self.emergency_relationship,
            'occupation': self.occupation,
            'employer': self.employer,
            'work_address': self.work_address,
            'work_phone': self.work_phone,
            'preferred_communication': self.preferred_communication,
            'notification_preferences': self.notification_preferences,
            'is_active': self.is_active,
            'is_primary_guardian': self.is_primary_guardian,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'children_count': len(self.get_children())
        }

    def __repr__(self):
        return f'<Parent {self.id}>'


class ParentStudentRelationship(db.Model):
    __tablename__ = 'parent_student_relationship'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    # Relationship details
    relationship_type = db.Column(db.String(50), nullable=False, default='parent')
    can_view_grades = db.Column(db.Boolean, default=True)
    can_view_attendance = db.Column(db.Boolean, default=True)
    can_view_fees = db.Column(db.Boolean, default=True)
    can_receive_notifications = db.Column(db.Boolean, default=True)
    can_communicate_teachers = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    is_emergency_contact = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = db.relationship('Parent', backref='parent_student_relationships')
    student = db.relationship('Student', backref='parent_student_relationships')

    __table_args__ = (
        db.UniqueConstraint('parent_id', 'student_id', name='unique_parent_student'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'parent_id': self.parent_id,
            'student_id': self.student_id,
            'relationship_type': self.relationship_type,
            'can_view_grades': self.can_view_grades,
            'can_view_attendance': self.can_view_attendance,
            'can_view_fees': self.can_view_fees,
            'can_receive_notifications': self.can_receive_notifications,
            'can_communicate_teachers': self.can_communicate_teachers,
            'is_active': self.is_active,
            'is_emergency_contact': self.is_emergency_contact,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<ParentStudentRelationship {self.parent_id}-{self.student_id} ({self.relationship_type})>'
