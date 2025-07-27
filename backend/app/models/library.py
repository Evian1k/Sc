from app import db
from datetime import datetime, timedelta
import uuid

class BookCategory(db.Model):
    __tablename__ = 'book_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # School relationship for multi-tenancy
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    code = db.Column(db.String(20))  # e.g., FIC for Fiction, SCI for Science
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    books = db.relationship('Book', backref='category', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'school_id': self.school_id,
            'name': self.name,
            'description': self.description,
            'code': self.code,
            'is_active': self.is_active,
            'books_count': self.books.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<BookCategory {self.name}>'


class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # School relationship for multi-tenancy
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    
    # Book Information
    isbn = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200))
    author = db.Column(db.String(200), nullable=False)
    co_authors = db.Column(db.Text)
    publisher = db.Column(db.String(100))
    publication_year = db.Column(db.Integer)
    edition = db.Column(db.String(50))
    language = db.Column(db.String(50), default='English')
    
    # Classification
    category_id = db.Column(db.Integer, db.ForeignKey('book_categories.id'))
    call_number = db.Column(db.String(50))  # Library classification number
    dewey_decimal = db.Column(db.String(20))
    
    # Physical Details
    pages = db.Column(db.Integer)
    dimensions = db.Column(db.String(50))  # e.g., "21cm x 15cm"
    weight = db.Column(db.String(20))
    binding = db.Column(db.String(20))  # hardcover, paperback, spiral
    
    # Content
    description = db.Column(db.Text)
    table_of_contents = db.Column(db.Text)
    keywords = db.Column(db.Text)  # Comma-separated keywords for search
    
    # Inventory
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    damaged_copies = db.Column(db.Integer, default=0)
    lost_copies = db.Column(db.Integer, default=0)
    
    # Pricing
    purchase_price = db.Column(db.Float)
    current_value = db.Column(db.Float)
    replacement_cost = db.Column(db.Float)
    
    # Location
    shelf_location = db.Column(db.String(50))
    section = db.Column(db.String(50))
    
    # Digital
    has_ebook = db.Column(db.Boolean, default=False)
    ebook_url = db.Column(db.String(255))
    cover_image_url = db.Column(db.String(255))
    
    # Rules
    loan_period_days = db.Column(db.Integer, default=14)
    max_renewals = db.Column(db.Integer, default=2)
    fine_per_day = db.Column(db.Float, default=10.0)  # Fine amount per day for late return
    
    # Status
    status = db.Column(db.String(20), default='available')  # available, checked_out, reserved, maintenance, lost
    is_active = db.Column(db.Boolean, default=True)
    is_reference_only = db.Column(db.Boolean, default=False)  # Cannot be borrowed
    
    # Timestamps
    acquired_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Audit trail
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    transactions = db.relationship('LibraryTransaction', backref='book', lazy='dynamic')
    reservations = db.relationship('BookReservation', backref='book', lazy='dynamic')
    
    def get_popularity_score(self):
        """Calculate book popularity based on transaction history"""
        return self.transactions.count()
    
    def is_available(self):
        """Check if book is available for borrowing"""
        return self.available_copies > 0 and self.status == 'available' and not self.is_reference_only
    
    def get_current_borrowers(self):
        """Get list of current borrowers"""
        return self.transactions.filter_by(status='borrowed').all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'school_id': self.school_id,
            'isbn': self.isbn,
            'title': self.title,
            'subtitle': self.subtitle,
            'author': self.author,
            'co_authors': self.co_authors,
            'publisher': self.publisher,
            'publication_year': self.publication_year,
            'edition': self.edition,
            'language': self.language,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'call_number': self.call_number,
            'dewey_decimal': self.dewey_decimal,
            'pages': self.pages,
            'dimensions': self.dimensions,
            'weight': self.weight,
            'binding': self.binding,
            'description': self.description,
            'keywords': self.keywords,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'damaged_copies': self.damaged_copies,
            'lost_copies': self.lost_copies,
            'purchase_price': self.purchase_price,
            'current_value': self.current_value,
            'replacement_cost': self.replacement_cost,
            'shelf_location': self.shelf_location,
            'section': self.section,
            'has_ebook': self.has_ebook,
            'ebook_url': self.ebook_url,
            'cover_image_url': self.cover_image_url,
            'loan_period_days': self.loan_period_days,
            'max_renewals': self.max_renewals,
            'fine_per_day': self.fine_per_day,
            'status': self.status,
            'is_active': self.is_active,
            'is_reference_only': self.is_reference_only,
            'is_available': self.is_available(),
            'popularity_score': self.get_popularity_score(),
            'acquired_date': self.acquired_date.isoformat() if self.acquired_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'


class LibraryTransaction(db.Model):
    __tablename__ = 'library_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    librarian_id = db.Column(db.Integer, db.ForeignKey('staff.id'))  # Staff who processed the transaction
    
    # Transaction Details
    transaction_type = db.Column(db.String(20), nullable=False)  # borrow, return, renew, reserve
    checkout_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(20), default='borrowed')  # borrowed, returned, overdue, lost, damaged
    
    # Renewal Information
    renewal_count = db.Column(db.Integer, default=0)
    max_renewals_allowed = db.Column(db.Integer, default=2)
    
    # Condition
    condition_on_checkout = db.Column(db.String(20), default='good')  # excellent, good, fair, poor
    condition_on_return = db.Column(db.String(20))
    
    # Fines and Penalties
    fine_amount = db.Column(db.Float, default=0.0)
    fine_paid = db.Column(db.Float, default=0.0)
    fine_waived = db.Column(db.Float, default=0.0)
    fine_reason = db.Column(db.String(100))  # late_return, damage, loss
    
    # Notes
    checkout_notes = db.Column(db.Text)
    return_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='library_transactions')
    librarian = db.relationship('Staff', backref='library_transactions')
    
    def calculate_fine(self):
        """Calculate fine for overdue books"""
        if self.status == 'returned' or not self.due_date:
            return 0
        
        now = datetime.utcnow()
        return_date = self.return_date if self.return_date else now
        
        if return_date > self.due_date:
            days_overdue = (return_date - self.due_date).days
            return days_overdue * self.book.fine_per_day
        return 0
    
    def is_overdue(self):
        """Check if the book is overdue"""
        if self.status == 'returned' or not self.due_date:
            return False
        return datetime.utcnow() > self.due_date
    
    def days_overdue(self):
        """Get number of days overdue"""
        if not self.is_overdue():
            return 0
        return (datetime.utcnow() - self.due_date).days
    
    def can_renew(self):
        """Check if the book can be renewed"""
        return (self.renewal_count < self.max_renewals_allowed and 
                self.status == 'borrowed' and 
                not self.is_overdue())
    
    def renew(self, additional_days=None):
        """Renew the book loan"""
        if not self.can_renew():
            return False
        
        days = additional_days or self.book.loan_period_days
        self.due_date = self.due_date + timedelta(days=days)
        self.renewal_count += 1
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'book_id': self.book_id,
            'student_id': self.student_id,
            'librarian_id': self.librarian_id,
            'book_title': self.book.title if self.book else None,
            'student_name': self.student.full_name if self.student else None,
            'librarian_name': self.librarian.user.get_full_name() if self.librarian and self.librarian.user else None,
            'transaction_type': self.transaction_type,
            'checkout_date': self.checkout_date.isoformat() if self.checkout_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'status': self.status,
            'renewal_count': self.renewal_count,
            'max_renewals_allowed': self.max_renewals_allowed,
            'condition_on_checkout': self.condition_on_checkout,
            'condition_on_return': self.condition_on_return,
            'fine_amount': self.fine_amount,
            'fine_paid': self.fine_paid,
            'fine_waived': self.fine_waived,
            'fine_reason': self.fine_reason,
            'checkout_notes': self.checkout_notes,
            'return_notes': self.return_notes,
            'is_overdue': self.is_overdue(),
            'days_overdue': self.days_overdue(),
            'can_renew': self.can_renew(),
            'current_fine': self.calculate_fine(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<LibraryTransaction {self.book.title if self.book else "Unknown"} - {self.student.full_name if self.student else "Unknown"}>'


class BookReservation(db.Model):
    __tablename__ = 'book_reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Reservation Details
    reservation_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)  # When the reservation expires
    notification_sent = db.Column(db.Boolean, default=False)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, fulfilled, expired, cancelled
    
    # Queue position
    queue_position = db.Column(db.Integer)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='book_reservations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'book_id': self.book_id,
            'student_id': self.student_id,
            'book_title': self.book.title if self.book else None,
            'student_name': self.student.full_name if self.student else None,
            'reservation_date': self.reservation_date.isoformat() if self.reservation_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'notification_sent': self.notification_sent,
            'status': self.status,
            'queue_position': self.queue_position,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<BookReservation {self.book.title if self.book else "Unknown"} - {self.student.full_name if self.student else "Unknown"}>'