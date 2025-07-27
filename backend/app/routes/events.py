from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Event, EventRegistration, DisciplinaryRecord, Student, Staff
from datetime import datetime

events_bp = Blueprint('events', __name__)

@events_bp.route('', methods=['GET'])
@jwt_required()
def get_events():
    """Get all events with filtering"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        event_type = request.args.get('type')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Event.query.filter_by(school_id=user.school_id)
        
        if event_type:
            query = query.filter_by(event_type=event_type)
        
        if status:
            query = query.filter_by(status=status)
        
        if start_date:
            query = query.filter(Event.start_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query = query.filter(Event.end_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        # Filter based on user role
        if user.role == 'student':
            # Students see only published events they can register for
            query = query.filter(
                Event.is_published == True,
                db.or_(
                    Event.target_audience.contains(['all']),
                    Event.target_audience.contains(['students'])
                )
            )
        
        events = query.order_by(Event.start_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'events': [event.to_dict() for event in events.items],
            'pagination': {
                'total': events.total,
                'pages': events.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('', methods=['POST'])
@jwt_required()
def create_event():
    """Create a new event"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'event_type', 'start_date', 'start_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        event = Event(
            school_id=user.school_id,
            title=data['title'],
            description=data.get('description'),
            event_type=data['event_type'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None,
            location=data.get('location'),
            venue_details=data.get('venue_details'),
            organizer_name=data.get('organizer_name'),
            organizer_contact=data.get('organizer_contact'),
            target_audience=data.get('target_audience', ['all']),
            max_participants=data.get('max_participants'),
            registration_required=data.get('registration_required', False),
            registration_deadline=datetime.strptime(data['registration_deadline'], '%Y-%m-%d').date() if data.get('registration_deadline') else None,
            registration_fee=data.get('registration_fee', 0),
            requirements=data.get('requirements'),
            dress_code=data.get('dress_code'),
            special_instructions=data.get('special_instructions'),
            created_by_id=user.id
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'message': 'Event created successfully',
            'event': event.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    """Get specific event details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        event = Event.query.get(event_id)
        if not event or event.school_id != user.school_id:
            return jsonify({'error': 'Event not found'}), 404
        
        # Check permissions for students
        if user.role == 'student' and not event.is_published:
            return jsonify({'error': 'Event not available'}), 403
        
        # Get user's registration status if applicable
        event_data = event.to_dict()
        
        if event.registration_required:
            registration = EventRegistration.query.filter_by(
                event_id=event_id, user_id=user.id
            ).first()
            
            event_data['user_registration'] = registration.to_dict() if registration else None
            
            # Get registration statistics for admins/teachers
            if user.role in ['admin', 'teacher']:
                total_registrations = EventRegistration.query.filter_by(event_id=event_id).count()
                confirmed_registrations = EventRegistration.query.filter_by(
                    event_id=event_id, status='confirmed'
                ).count()
                
                event_data['registration_stats'] = {
                    'total_registrations': total_registrations,
                    'confirmed_registrations': confirmed_registrations,
                    'available_spots': (event.max_participants - confirmed_registrations) if event.max_participants else None
                }
        
        return jsonify({'event': event_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """Update event information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        event = Event.query.get(event_id)
        if not event or event.school_id != user.school_id:
            return jsonify({'error': 'Event not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        updatable_fields = [
            'title', 'description', 'event_type', 'location', 'venue_details',
            'organizer_name', 'organizer_contact', 'target_audience', 'max_participants',
            'registration_required', 'registration_fee', 'requirements', 'dress_code',
            'special_instructions'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(event, field, data[field])
        
        # Handle date and time fields
        if 'start_date' in data:
            event.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        
        if 'end_date' in data and data['end_date']:
            event.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        if 'start_time' in data:
            event.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        
        if 'end_time' in data and data['end_time']:
            event.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        if 'registration_deadline' in data and data['registration_deadline']:
            event.registration_deadline = datetime.strptime(data['registration_deadline'], '%Y-%m-%d').date()
        
        event.updated_by_id = user.id
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Event updated successfully',
            'event': event.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<int:event_id>/publish', methods=['POST'])
@jwt_required()
def publish_event(event_id):
    """Publish an event"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        event = Event.query.get(event_id)
        if not event or event.school_id != user.school_id:
            return jsonify({'error': 'Event not found'}), 404
        
        event.is_published = True
        event.status = 'active'
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Send notifications to target audience
        from app.services.notification_service import notification_service
        
        notification_service.send_broadcast_message(
            user.school_id,
            event.target_audience,
            f'New Event: {event.title}',
            f'A new event "{event.title}" has been scheduled for {event.start_date}. Check the events calendar for details.'
        )
        
        return jsonify({
            'message': 'Event published successfully',
            'event': event.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<int:event_id>/register', methods=['POST'])
@jwt_required()
def register_for_event(event_id):
    """Register for an event"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        event = Event.query.get(event_id)
        if not event or event.school_id != user.school_id:
            return jsonify({'error': 'Event not found'}), 404
        
        if not event.is_published:
            return jsonify({'error': 'Event not available for registration'}), 403
        
        if not event.registration_required:
            return jsonify({'error': 'Registration not required for this event'}), 400
        
        # Check if registration deadline has passed
        if event.registration_deadline and datetime.now().date() > event.registration_deadline:
            return jsonify({'error': 'Registration deadline has passed'}), 400
        
        # Check if already registered
        existing_registration = EventRegistration.query.filter_by(
            event_id=event_id, user_id=user.id
        ).first()
        
        if existing_registration:
            return jsonify({'error': 'Already registered for this event'}), 409
        
        # Check if event is full
        if event.max_participants:
            confirmed_count = EventRegistration.query.filter_by(
                event_id=event_id, status='confirmed'
            ).count()
            
            if confirmed_count >= event.max_participants:
                return jsonify({'error': 'Event is full'}), 400
        
        data = request.get_json() or {}
        
        registration = EventRegistration(
            event_id=event_id,
            user_id=user.id,
            registration_date=datetime.now().date(),
            status='pending',
            comments=data.get('comments'),
            emergency_contact=data.get('emergency_contact'),
            dietary_requirements=data.get('dietary_requirements'),
            special_needs=data.get('special_needs')
        )
        
        db.session.add(registration)
        db.session.commit()
        
        return jsonify({
            'message': 'Registration submitted successfully',
            'registration': registration.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<int:event_id>/registrations', methods=['GET'])
@jwt_required()
def get_event_registrations(event_id):
    """Get event registrations (admin/teacher only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        event = Event.query.get(event_id)
        if not event or event.school_id != user.school_id:
            return jsonify({'error': 'Event not found'}), 404
        
        registrations = EventRegistration.query.filter_by(event_id=event_id).all()
        
        return jsonify({
            'registrations': [reg.to_dict() for reg in registrations],
            'total': len(registrations)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/calendar', methods=['GET'])
@jwt_required()
def get_event_calendar():
    """Get events for calendar view"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # Get events for the specified month
        from datetime import date
        start_date = date(year, month, 1)
        
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        query = Event.query.filter(
            Event.school_id == user.school_id,
            Event.start_date >= start_date,
            Event.start_date < end_date
        )
        
        # Filter by user role
        if user.role == 'student':
            query = query.filter(
                Event.is_published == True,
                db.or_(
                    Event.target_audience.contains(['all']),
                    Event.target_audience.contains(['students'])
                )
            )
        
        events = query.order_by(Event.start_date).all()
        
        # Group events by date
        calendar_events = {}
        for event in events:
            date_str = event.start_date.isoformat()
            if date_str not in calendar_events:
                calendar_events[date_str] = []
            
            calendar_events[date_str].append({
                'id': event.id,
                'title': event.title,
                'event_type': event.event_type,
                'start_time': event.start_time.strftime('%H:%M') if event.start_time else None,
                'end_time': event.end_time.strftime('%H:%M') if event.end_time else None,
                'location': event.location,
                'status': event.status
            })
        
        return jsonify({
            'calendar': calendar_events,
            'year': year,
            'month': month
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/types', methods=['GET'])
@jwt_required()
def get_event_types():
    """Get available event types"""
    try:
        event_types = [
            {'id': 'academic', 'name': 'Academic', 'description': 'Academic events like exams, seminars'},
            {'id': 'sports', 'name': 'Sports', 'description': 'Sports and games events'},
            {'id': 'cultural', 'name': 'Cultural', 'description': 'Cultural and arts events'},
            {'id': 'social', 'name': 'Social', 'description': 'Social gatherings and celebrations'},
            {'id': 'meeting', 'name': 'Meeting', 'description': 'Official meetings and assemblies'},
            {'id': 'holiday', 'name': 'Holiday', 'description': 'Holidays and breaks'},
            {'id': 'training', 'name': 'Training', 'description': 'Training and workshops'},
            {'id': 'other', 'name': 'Other', 'description': 'Other events'}
        ]
        
        return jsonify({'event_types': event_types})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Disciplinary Records Management
@events_bp.route('/disciplinary', methods=['GET'])
@jwt_required()
def get_disciplinary_records():
    """Get disciplinary records"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Build query based on user role
        query = DisciplinaryRecord.query.filter_by(school_id=user.school_id)
        
        if user.role == 'student':
            # Students see only their own records
            student = Student.query.filter_by(user_id=user.id).first()
            if student:
                query = query.filter_by(student_id=student.id)
            else:
                return jsonify({'disciplinary_records': [], 'total': 0})
        
        elif user.role == 'teacher':
            # Teachers see records they reported
            query = query.filter_by(reported_by_id=user.id)
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        severity = request.args.get('severity')
        status = request.args.get('status')
        
        if severity:
            query = query.filter_by(severity=severity)
        
        if status:
            query = query.filter_by(status=status)
        
        records = query.order_by(DisciplinaryRecord.incident_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'disciplinary_records': [record.to_dict() for record in records.items],
            'pagination': {
                'total': records.total,
                'pages': records.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@events_bp.route('/disciplinary', methods=['POST'])
@jwt_required()
def create_disciplinary_record():
    """Create a disciplinary record"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_id', 'incident_type', 'description', 'incident_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify student belongs to the same school
        student = Student.query.get(data['student_id'])
        if not student or student.school_id != user.school_id:
            return jsonify({'error': 'Student not found'}), 404
        
        record = DisciplinaryRecord(
            school_id=user.school_id,
            student_id=data['student_id'],
            incident_type=data['incident_type'],
            description=data['description'],
            incident_date=datetime.strptime(data['incident_date'], '%Y-%m-%d').date(),
            incident_time=datetime.strptime(data['incident_time'], '%H:%M').time() if data.get('incident_time') else None,
            location=data.get('location'),
            severity=data.get('severity', 'Minor'),
            witnesses=data.get('witnesses'),
            action_taken=data.get('action_taken'),
            follow_up_required=data.get('follow_up_required', False),
            follow_up_date=datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date() if data.get('follow_up_date') else None,
            parent_notified=data.get('parent_notified', False),
            parent_contact_date=datetime.strptime(data['parent_contact_date'], '%Y-%m-%d').date() if data.get('parent_contact_date') else None,
            reported_by_id=user.id
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'message': 'Disciplinary record created successfully',
            'record': record.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500