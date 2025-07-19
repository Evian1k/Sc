from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.fee import Fee
from app.models.student import Student
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func

fees_bp = Blueprint('fees', __name__)

@fees_bp.route('/', methods=['GET'])
@jwt_required()
def get_fees():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        student_id = request.args.get('student_id', type=int)
        class_id = request.args.get('class_id', type=int)
        fee_type = request.args.get('fee_type')
        status = request.args.get('status')
        semester = request.args.get('semester')
        academic_year = request.args.get('academic_year')
        
        query = Fee.query.join(Student)
        
        if student_id:
            query = query.filter(Fee.student_id == student_id)
        
        if class_id:
            query = query.filter(Student.class_id == class_id)
        
        if fee_type:
            query = query.filter(Fee.fee_type == fee_type)
        
        if status:
            query = query.filter(Fee.status == status)
        
        if semester:
            query = query.filter(Fee.semester == semester)
        
        if academic_year:
            query = query.filter(Fee.academic_year == academic_year)
        
        fees = query.order_by(Fee.due_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'fees': [fee.to_dict() for fee in fees.items],
            'total': fees.total,
            'pages': fees.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fees_bp.route('/<int:fee_id>', methods=['GET'])
@jwt_required()
def get_fee(fee_id):
    try:
        fee = Fee.query.get_or_404(fee_id)
        return jsonify(fee.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fees_bp.route('/', methods=['POST'])
@jwt_required()
def create_fee():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        fee = Fee(
            student_id=data.get('student_id'),
            fee_type=data.get('fee_type'),
            amount=Decimal(str(data.get('amount'))),
            due_date=datetime.strptime(data.get('due_date'), '%Y-%m-%d').date(),
            semester=data.get('semester'),
            academic_year=data.get('academic_year'),
            late_fee=Decimal(str(data.get('late_fee', 0))),
            discount=Decimal(str(data.get('discount', 0))),
            notes=data.get('notes', '')
        )
        
        fee.update_status()
        
        db.session.add(fee)
        db.session.commit()
        
        return jsonify({'message': 'Fee record created successfully', 'fee': fee.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fees_bp.route('/<int:fee_id>', methods=['PUT'])
@jwt_required()
def update_fee(fee_id):
    try:
        fee = Fee.query.get_or_404(fee_id)
        data = request.get_json()
        
        # Update fields
        for field in ['fee_type', 'semester', 'academic_year', 'notes']:
            if field in data:
                setattr(fee, field, data[field])
        
        if 'amount' in data:
            fee.amount = Decimal(str(data['amount']))
        
        if 'due_date' in data:
            fee.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        
        if 'late_fee' in data:
            fee.late_fee = Decimal(str(data['late_fee']))
        
        if 'discount' in data:
            fee.discount = Decimal(str(data['discount']))
        
        fee.update_status()
        
        db.session.commit()
        
        return jsonify({'message': 'Fee record updated successfully', 'fee': fee.to_dict()}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fees_bp.route('/<int:fee_id>', methods=['DELETE'])
@jwt_required()
def delete_fee(fee_id):
    try:
        fee = Fee.query.get_or_404(fee_id)
        db.session.delete(fee)
        db.session.commit()
        
        return jsonify({'message': 'Fee record deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fees_bp.route('/<int:fee_id>/payment', methods=['POST'])
@jwt_required()
def record_payment(fee_id):
    try:
        fee = Fee.query.get_or_404(fee_id)
        data = request.get_json()
        user_id = get_jwt_identity()
        
        payment_amount = Decimal(str(data.get('payment_amount')))
        payment_method = data.get('payment_method')
        transaction_id = data.get('transaction_id', '')
        payment_date = data.get('payment_date')
        
        if payment_date:
            fee.payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
        else:
            fee.payment_date = date.today()
        
        # Update paid amount
        fee.paid_amount = (fee.paid_amount or 0) + payment_amount
        fee.payment_method = payment_method
        fee.transaction_id = transaction_id
        fee.collected_by = user_id
        
        # Update status based on payment
        fee.update_status()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment recorded successfully',
            'fee': fee.to_dict(),
            'payment_amount': float(payment_amount),
            'remaining_balance': fee.balance_amount
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fees_bp.route('/bulk-create', methods=['POST'])
@jwt_required()
def bulk_create_fees():
    try:
        data = request.get_json()
        fees_data = data.get('fees', [])
        user_id = get_jwt_identity()
        
        created_fees = []
        errors = []
        
        for idx, fee_data in enumerate(fees_data):
            try:
                fee = Fee(
                    student_id=fee_data.get('student_id'),
                    fee_type=fee_data.get('fee_type'),
                    amount=Decimal(str(fee_data.get('amount'))),
                    due_date=datetime.strptime(fee_data.get('due_date'), '%Y-%m-%d').date(),
                    semester=fee_data.get('semester'),
                    academic_year=fee_data.get('academic_year'),
                    late_fee=Decimal(str(fee_data.get('late_fee', 0))),
                    discount=Decimal(str(fee_data.get('discount', 0))),
                    notes=fee_data.get('notes', '')
                )
                
                fee.update_status()
                
                db.session.add(fee)
                created_fees.append(fee.to_dict())
                
            except Exception as e:
                errors.append({'row': idx + 1, 'error': str(e)})
        
        if not errors:
            db.session.commit()
        else:
            db.session.rollback()
        
        return jsonify({
            'message': f'Created {len(created_fees)} fee records successfully',
            'created_fees': created_fees,
            'errors': errors
        }), 201 if not errors else 400
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fees_bp.route('/student/<int:student_id>/summary', methods=['GET'])
@jwt_required()
def student_fee_summary(student_id):
    try:
        semester = request.args.get('semester')
        academic_year = request.args.get('academic_year')
        
        query = Fee.query.filter_by(student_id=student_id)
        
        if semester:
            query = query.filter(Fee.semester == semester)
        
        if academic_year:
            query = query.filter(Fee.academic_year == academic_year)
        
        fees = query.all()
        
        # Calculate summary statistics
        total_amount = sum(fee.amount for fee in fees)
        total_paid = sum(fee.paid_amount for fee in fees)
        total_discount = sum(fee.discount for fee in fees)
        total_late_fee = sum(fee.late_fee for fee in fees)
        total_balance = sum(fee.balance_amount for fee in fees)
        
        # Group by status
        status_summary = {}
        for fee in fees:
            status = fee.status
            if status not in status_summary:
                status_summary[status] = {'count': 0, 'amount': 0}
            status_summary[status]['count'] += 1
            status_summary[status]['amount'] += float(fee.amount)
        
        # Group by fee type
        fee_type_summary = {}
        for fee in fees:
            fee_type = fee.fee_type
            if fee_type not in fee_type_summary:
                fee_type_summary[fee_type] = {'count': 0, 'amount': 0, 'paid': 0, 'balance': 0}
            fee_type_summary[fee_type]['count'] += 1
            fee_type_summary[fee_type]['amount'] += float(fee.amount)
            fee_type_summary[fee_type]['paid'] += float(fee.paid_amount or 0)
            fee_type_summary[fee_type]['balance'] += fee.balance_amount
        
        return jsonify({
            'student_id': student_id,
            'fees': [fee.to_dict() for fee in fees],
            'summary': {
                'total_fees': len(fees),
                'total_amount': float(total_amount),
                'total_paid': float(total_paid),
                'total_discount': float(total_discount),
                'total_late_fee': float(total_late_fee),
                'total_balance': float(total_balance)
            },
            'status_summary': status_summary,
            'fee_type_summary': fee_type_summary,
            'filters': {
                'semester': semester,
                'academic_year': academic_year
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fees_bp.route('/report', methods=['GET'])
@jwt_required()
def fee_collection_report():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        class_id = request.args.get('class_id', type=int)
        fee_type = request.args.get('fee_type')
        status = request.args.get('status')
        
        query = Fee.query.join(Student)
        
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Fee.payment_date.between(start_date, end_date))
        
        if class_id:
            query = query.filter(Student.class_id == class_id)
        
        if fee_type:
            query = query.filter(Fee.fee_type == fee_type)
        
        if status:
            query = query.filter(Fee.status == status)
        
        fees = query.all()
        
        # Calculate report statistics
        total_fees = len(fees)
        total_amount_due = sum(fee.amount for fee in fees)
        total_collected = sum(fee.paid_amount or 0 for fee in fees)
        total_outstanding = sum(fee.balance_amount for fee in fees)
        
        # Collection by fee type
        fee_type_collection = {}
        for fee in fees:
            fee_type = fee.fee_type
            if fee_type not in fee_type_collection:
                fee_type_collection[fee_type] = {
                    'count': 0,
                    'amount_due': 0,
                    'collected': 0,
                    'outstanding': 0
                }
            fee_type_collection[fee_type]['count'] += 1
            fee_type_collection[fee_type]['amount_due'] += float(fee.amount)
            fee_type_collection[fee_type]['collected'] += float(fee.paid_amount or 0)
            fee_type_collection[fee_type]['outstanding'] += fee.balance_amount
        
        # Collection by status
        status_collection = {}
        for fee in fees:
            status = fee.status
            if status not in status_collection:
                status_collection[status] = {'count': 0, 'amount': 0}
            status_collection[status]['count'] += 1
            status_collection[status]['amount'] += float(fee.amount)
        
        return jsonify({
            'report': [fee.to_dict() for fee in fees],
            'summary': {
                'total_fees': total_fees,
                'total_amount_due': float(total_amount_due),
                'total_collected': float(total_collected),
                'total_outstanding': float(total_outstanding),
                'collection_percentage': round((total_collected / total_amount_due * 100), 2) if total_amount_due > 0 else 0
            },
            'fee_type_collection': fee_type_collection,
            'status_collection': status_collection,
            'filters': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'class_id': class_id,
                'fee_type': fee_type,
                'status': status
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fees_bp.route('/overdue', methods=['GET'])
@jwt_required()
def get_overdue_fees():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get fees where due date has passed and status is not paid
        overdue_fees = Fee.query.filter(
            Fee.due_date < date.today(),
            Fee.status.in_(['pending', 'partial'])
        ).join(Student).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'overdue_fees': [fee.to_dict() for fee in overdue_fees.items],
            'total': overdue_fees.total,
            'pages': overdue_fees.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500