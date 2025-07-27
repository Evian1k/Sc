from app import db
from datetime import datetime
import uuid

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # School relationship for multi-tenancy
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    
    # Event Information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50), nullable=False)  # academic, sports, cultural, meeting, holiday, exam
    category = db.Column(db.String(50))  # parent-meeting, sports-day, graduation, etc.
    
    # Timing
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    all_day = db.Column(db.Boolean, default=False)
    
    # Location
    venue = db.Column(db.String(200))
    location_details = db.Column(db.Text)
    
    # Participants
    target_audience = db.Column(db.String(50))  # all, students, teachers, parents, specific_class
    specific_classes = db.Column(db.JSON)  # List of class IDs if target_audience is specific_class
    max_participants = db.Column(db.Integer)
    registration_required = db.Column(db.Boolean, default=False)
    registration_deadline = db.Column(db.DateTime)
    
    # Event Management
    organizer_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    
    # Status and Visibility
    status = db.Column(db.String(20), default='draft')  # draft, published, ongoing, completed, cancelled
    is_public = db.Column(db.Boolean, default=True)
    send_notifications = db.Column(db.Boolean, default=True)
    
    # Additional Information
    instructions = db.Column(db.Text)
    requirements = db.Column(db.Text)
    dress_code = db.Column(db.String(100))
    cost = db.Column(db.Float, default=0.0)
    
    # Recurring Events
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(20))  # daily, weekly, monthly, yearly
    recurrence_end = db.Column(db.Date)
    
    # Files and Links
    attachment_url = db.Column(db.String(255))
    external_link = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit trail
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    organizer = db.relationship('Staff', backref='organized_events')
    registrations = db.relationship('EventRegistration', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_registration_count(self):
        """Get number of registrations for this event"""
        return self.registrations.filter_by(status='confirmed').count()
    
    def is_registration_open(self):
        """Check if registration is still open"""
        if not self.registration_required:
            return False
        if self.registration_deadline and datetime.utcnow() > self.registration_deadline:
            return False
        if self.max_participants and self.get_registration_count() >= self.max_participants:
            return False
        return self.status == 'published'
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'school_id': self.school_id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type,
            'category': self.category,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'all_day': self.all_day,
            'venue': self.venue,
            'location_details': self.location_details,
            'target_audience': self.target_audience,
            'specific_classes': self.specific_classes,
            'max_participants': self.max_participants,
            'registration_required': self.registration_required,
            'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            'organizer_id': self.organizer_id,
            'organizer_name': self.organizer.user.get_full_name() if self.organizer and self.organizer.user else None,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'status': self.status,
            'is_public': self.is_public,
            'send_notifications': self.send_notifications,
            'instructions': self.instructions,
            'requirements': self.requirements,
            'dress_code': self.dress_code,
            'cost': self.cost,
            'is_recurring': self.is_recurring,
            'recurrence_pattern': self.recurrence_pattern,
            'recurrence_end': self.recurrence_end.isoformat() if self.recurrence_end else None,
            'attachment_url': self.attachment_url,
            'external_link': self.external_link,
            'registration_count': self.get_registration_count(),
            'is_registration_open': self.is_registration_open(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Event {self.title} ({self.start_date})>'


class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Can be student, parent, or staff
    
    # Registration Details
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, attended
    
    # Additional Information
    notes = db.Column(db.Text)
    special_requirements = db.Column(db.Text)
    
    # Payment (if event has cost)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, refunded
    payment_amount = db.Column(db.Float, default=0.0)
    payment_date = db.Column(db.DateTime)
    
    # Attendance
    attended = db.Column(db.Boolean, default=False)
    attendance_time = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='event_registrations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'user_name': self.user.get_full_name() if self.user else None,
            'user_role': self.user.role if self.user else None,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'status': self.status,
            'notes': self.notes,
            'special_requirements': self.special_requirements,
            'payment_status': self.payment_status,
            'payment_amount': self.payment_amount,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'attended': self.attended,
            'attendance_time': self.attendance_time.isoformat() if self.attendance_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<EventRegistration {self.event.title if self.event else "Unknown"} - {self.user.get_full_name() if self.user else "Unknown"}>'


class DisciplinaryRecord(db.Model):
    __tablename__ = 'disciplinary_records'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    reported_by_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    handled_by_id = db.Column(db.Integer, db.ForeignKey('staff.id'))  # Who handled the case
    
    # Incident Information
    incident_date = db.Column(db.DateTime, nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)  # misconduct, absence, lateness, academic, other
    severity = db.Column(db.String(20), default='minor')  # minor, major, severe
    category = db.Column(db.String(50))  # fighting, cheating, disrespect, etc.
    
    # Details
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100))
    witnesses = db.Column(db.Text)
    evidence = db.Column(db.Text)
    
    # Action Taken
    action_taken = db.Column(db.String(50))  # warning, detention, suspension, expulsion, counseling
    action_description = db.Column(db.Text)
    action_date = db.Column(db.DateTime)
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)
    
    # Parent Communication
    parent_notified = db.Column(db.Boolean, default=False)
    parent_notification_date = db.Column(db.DateTime)
    parent_response = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='open')  # open, resolved, closed, under_review
    resolution_notes = db.Column(db.Text)
    
    # Files
    attachment_urls = db.Column(db.JSON)  # List of file URLs
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reported_by = db.relationship('Staff', foreign_keys=[reported_by_id], backref='reported_disciplinary_records')
    handled_by = db.relationship('Staff', foreign_keys=[handled_by_id], backref='handled_disciplinary_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'reported_by_id': self.reported_by_id,
            'reported_by_name': self.reported_by.user.get_full_name() if self.reported_by and self.reported_by.user else None,
            'handled_by_id': self.handled_by_id,
            'handled_by_name': self.handled_by.user.get_full_name() if self.handled_by and self.handled_by.user else None,
            'incident_date': self.incident_date.isoformat() if self.incident_date else None,
            'incident_type': self.incident_type,
            'severity': self.severity,
            'category': self.category,
            'description': self.description,
            'location': self.location,
            'witnesses': self.witnesses,
            'evidence': self.evidence,
            'action_taken': self.action_taken,
            'action_description': self.action_description,
            'action_date': self.action_date.isoformat() if self.action_date else None,
            'follow_up_required': self.follow_up_required,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'parent_notified': self.parent_notified,
            'parent_notification_date': self.parent_notification_date.isoformat() if self.parent_notification_date else None,
            'parent_response': self.parent_response,
            'status': self.status,
            'resolution_notes': self.resolution_notes,
            'attachment_urls': self.attachment_urls,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<DisciplinaryRecord {self.student.full_name if self.student else "Unknown"} - {self.incident_type} ({self.incident_date})>'


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # School relationship for multi-tenancy
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    
    # Message Details
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # For direct messages
    
    # Message Content
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='direct')  # direct, broadcast, announcement, emergency
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Recipient Groups (for broadcast messages)
    recipient_groups = db.Column(db.JSON)  # e.g., ['all_students', 'class_1a', 'all_parents']
    
    # Delivery Options
    send_via_email = db.Column(db.Boolean, default=True)
    send_via_sms = db.Column(db.Boolean, default=False)
    send_via_app = db.Column(db.Boolean, default=True)
    send_via_whatsapp = db.Column(db.Boolean, default=False)
    
    # Scheduling
    send_immediately = db.Column(db.Boolean, default=True)
    scheduled_send_time = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, sent, delivered, failed
    
    # Read Status
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    
    # Delivery Tracking
    delivery_status = db.Column(db.JSON, default=lambda: {
        'email': 'pending',
        'sms': 'pending',
        'app': 'pending',
        'whatsapp': 'pending'
    })
    
    # Files
    attachment_urls = db.Column(db.JSON)  # List of file URLs
    
    # Thread (for replies)
    parent_message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    thread_id = db.Column(db.String(36))  # Groups related messages
    
    # Timestamps
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    parent_message = db.relationship('Message', remote_side=[id], backref='replies')
    
    def mark_as_read(self):
        """Mark message as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        db.session.commit()
    
    def get_recipients_count(self):
        """Get estimated number of recipients for broadcast messages"""
        if self.message_type == 'direct':
            return 1
        
        # This would need to be implemented based on actual recipient groups
        # For now, return a placeholder
        return len(self.recipient_groups) if self.recipient_groups else 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'school_id': self.school_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.get_full_name() if self.sender else None,
            'sender_role': self.sender.role if self.sender else None,
            'recipient_id': self.recipient_id,
            'recipient_name': self.recipient.get_full_name() if self.recipient else None,
            'subject': self.subject,
            'content': self.content,
            'message_type': self.message_type,
            'priority': self.priority,
            'recipient_groups': self.recipient_groups,
            'send_via_email': self.send_via_email,
            'send_via_sms': self.send_via_sms,
            'send_via_app': self.send_via_app,
            'send_via_whatsapp': self.send_via_whatsapp,
            'send_immediately': self.send_immediately,
            'scheduled_send_time': self.scheduled_send_time.isoformat() if self.scheduled_send_time else None,
            'status': self.status,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'delivery_status': self.delivery_status,
            'attachment_urls': self.attachment_urls,
            'parent_message_id': self.parent_message_id,
            'thread_id': self.thread_id,
            'recipients_count': self.get_recipients_count(),
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Message {self.subject[:50]}... from {self.sender.get_full_name() if self.sender else "Unknown"}>'