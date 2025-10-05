from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.school import School
from app.models.user import User
from . import require_role, current_user

schools_bp = Blueprint('schools', __name__)

@schools_bp.route('/', methods=['GET'])
@jwt_required()
@require_role('platform_owner')
def list_schools():
    schools = School.query.order_by(School.created_at.desc()).all()
    return jsonify([s.to_dict() for s in schools]), 200

@schools_bp.route('/', methods=['POST'])
@jwt_required()
@require_role('platform_owner')
def create_school():
    data = request.get_json()
    school = School(
        name=data.get('name'),
        subdomain=data.get('subdomain'),
        plan=data.get('plan', 'basic'),
        status=data.get('status', 'active'),
        address=data.get('address'),
        country=data.get('country'),
    )
    db.session.add(school)
    db.session.commit()
    return jsonify({'message': 'School created', 'school': school.to_dict()}), 201

@schools_bp.route('/<int:school_id>', methods=['PUT'])
@jwt_required()
@require_role('platform_owner')
def update_school(school_id):
    school = School.query.get_or_404(school_id)
    data = request.get_json()
    for field in ['name', 'subdomain', 'plan', 'status', 'address', 'country']:
        if field in data:
            setattr(school, field, data[field])
    db.session.commit()
    return jsonify({'message': 'School updated', 'school': school.to_dict()}), 200

@schools_bp.route('/<int:school_id>/suspend', methods=['POST'])
@jwt_required()
@require_role('platform_owner')
def suspend_school(school_id):
    school = School.query.get_or_404(school_id)
    school.status = 'suspended'
    db.session.commit()
    return jsonify({'message': 'School suspended'}), 200

@schools_bp.route('/<int:school_id>/reactivate', methods=['POST'])
@jwt_required()
@require_role('platform_owner')
def reactivate_school(school_id):
    school = School.query.get_or_404(school_id)
    school.status = 'active'
    db.session.commit()
    return jsonify({'message': 'School reactivated'}), 200
