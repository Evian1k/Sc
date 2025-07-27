from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Message
from datetime import datetime

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('', methods=['GET'])
@jwt_required()
def get_messages():
    """Get messages for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get messages where user is recipient or sender
        messages = Message.query.filter(
            db.or_(
                Message.recipient_id == user.id,
                Message.sender_id == user.id
            )
        ).order_by(Message.created_at.desc()).all()

        return jsonify({
            'messages': [message.to_dict() for message in messages],
            'total': len(messages)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@messages_bp.route('', methods=['POST'])
@jwt_required()
def send_message():
    """Send a new message"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        message = Message(
            sender_id=user.id,
            recipient_id=data.get('recipient_id'),
            subject=data.get('subject'),
            content=data.get('content'),
            school_id=user.school_id,
            message_type=data.get('message_type', 'general'),
            priority=data.get('priority', 'normal')
        )

        db.session.add(message)
        db.session.commit()

        return jsonify({
            'message': 'Message sent successfully',
            'data': message.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500