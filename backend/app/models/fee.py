from app import db
from datetime import datetime

class Fee(db.Model):
    __tablename__ = 'fees'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    fee_type = db.Column(db.String(50), nullable=False)  # tuition, library, lab, transport, etc.
    amount = db.Column(db.Decimal(10, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid_amount = db.Column(db.Decimal(10, 2), default=0)
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))  # cash, card, online, bank_transfer
    transaction_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, paid, partial, overdue
    semester = db.Column(db.String(20))
    academic_year = db.Column(db.String(20))
    late_fee = db.Column(db.Decimal(10, 2), default=0)
    discount = db.Column(db.Decimal(10, 2), default=0)
    notes = db.Column(db.Text)
    collected_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    collector = db.relationship('User', foreign_keys=[collected_by])
    
    @property
    def balance_amount(self):
        return float(self.amount + self.late_fee - self.discount - self.paid_amount)
    
    def update_status(self):
        if self.paid_amount >= (self.amount + self.late_fee - self.discount):
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        elif self.due_date < datetime.utcnow().date():
            self.status = 'overdue'
        else:
            self.status = 'pending'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'student_student_id': self.student.student_id if self.student else None,
            'fee_type': self.fee_type,
            'amount': float(self.amount) if self.amount else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_amount': float(self.paid_amount) if self.paid_amount else None,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'semester': self.semester,
            'academic_year': self.academic_year,
            'late_fee': float(self.late_fee) if self.late_fee else None,
            'discount': float(self.discount) if self.discount else None,
            'balance_amount': self.balance_amount,
            'notes': self.notes,
            'collected_by': self.collected_by,
            'collector_name': self.collector.username if self.collector else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }