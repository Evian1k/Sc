from app import db
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Numeric

class Fee(db.Model):
    __tablename__ = 'fees'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    fee_type = db.Column(db.String(50), nullable=False)  # tuition, library, transport, etc.
    amount = db.Column(Numeric(10, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    paid_amount = db.Column(Numeric(10, 2), default=0)
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))  # cash, cheque, online, etc.
    transaction_id = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    academic_year = db.Column(db.String(10), nullable=False)
    semester = db.Column(db.String(20))
    late_fee = db.Column(Numeric(10, 2), default=0)
    discount = db.Column(Numeric(10, 2), default=0)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue, partial
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def balance_amount(self):
        return float(self.amount + self.late_fee - self.discount - self.paid_amount)
    
    @property
    def is_overdue(self):
        return self.due_date < date.today() and self.status != 'paid'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'fee_type': self.fee_type,
            'amount': float(self.amount),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_amount': float(self.paid_amount),
            'balance_amount': self.balance_amount,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'remarks': self.remarks,
            'academic_year': self.academic_year,
            'semester': self.semester,
            'late_fee': float(self.late_fee),
            'discount': float(self.discount),
            'status': self.status,
            'is_overdue': self.is_overdue,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_status(self):
        """Update fee status based on payment"""
        if self.paid_amount >= self.amount + self.late_fee - self.discount:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        elif self.is_overdue:
            self.status = 'overdue'
        else:
            self.status = 'pending'
    
    def calculate_late_fee(self, daily_rate=Decimal('10.00')):
        """Calculate late fee based on overdue days"""
        if self.is_overdue and self.status != 'paid':
            overdue_days = (date.today() - self.due_date).days
            self.late_fee = float(daily_rate * overdue_days)
        return self.late_fee