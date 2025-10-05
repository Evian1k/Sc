from app import db
from datetime import datetime


class School(db.Model):
    __tablename__ = 'schools'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    subdomain = db.Column(db.String(255), unique=True)
    plan = db.Column(db.String(50), default='basic')  # basic, pro, enterprise
    status = db.Column(db.String(50), default='active')  # active, suspended, pending
    address = db.Column(db.Text)
    country = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subdomain': self.subdomain,
            'plan': self.plan,
            'status': self.status,
            'address': self.address,
            'country': self.country,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
