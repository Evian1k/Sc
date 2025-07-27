from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, BookCategory, Book, LibraryTransaction, BookReservation, Student, Staff
from datetime import datetime, timedelta

library_bp = Blueprint('library', __name__)

@library_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all book categories"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        categories = BookCategory.query.filter_by(school_id=user.school_id, is_active=True).all()
        
        return jsonify({
            'categories': [category.to_dict() for category in categories],
            'total': len(categories)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@library_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    """Create a new book category"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Category name is required'}), 400
        
        # Check if category already exists
        existing = BookCategory.query.filter_by(
            school_id=user.school_id, name=data['name']
        ).first()
        
        if existing:
            return jsonify({'error': 'Category already exists'}), 409
        
        category = BookCategory(
            school_id=user.school_id,
            name=data['name'],
            description=data.get('description'),
            color=data.get('color', '#3B82F6')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@library_bp.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    """Get all books with filtering and pagination"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category_id = request.args.get('category_id', type=int)
        search = request.args.get('search', '')
        availability = request.args.get('availability')  # available, borrowed, reserved
        
        # Build query
        query = Book.query.filter_by(school_id=user.school_id, is_active=True)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if search:
            query = query.filter(
                db.or_(
                    Book.title.ilike(f'%{search}%'),
                    Book.author.ilike(f'%{search}%'),
                    Book.isbn.ilike(f'%{search}%')
                )
            )
        
        if availability == 'available':
            query = query.filter(Book.copies_available > 0)
        elif availability == 'borrowed':
            query = query.filter(Book.copies_available < Book.total_copies)
        
        books = query.order_by(Book.title).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'books': [book.to_dict() for book in books.items],
            'pagination': {
                'total': books.total,
                'pages': books.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@library_bp.route('/books', methods=['POST'])
@jwt_required()
def add_book():
    """Add a new book to the library"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'author', 'isbn', 'category_id', 'total_copies']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if ISBN already exists
        existing = Book.query.filter_by(
            school_id=user.school_id, isbn=data['isbn']
        ).first()
        
        if existing:
            return jsonify({'error': 'Book with this ISBN already exists'}), 409
        
        book = Book(
            school_id=user.school_id,
            category_id=data['category_id'],
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            publisher=data.get('publisher'),
            publication_year=data.get('publication_year'),
            edition=data.get('edition'),
            language=data.get('language', 'English'),
            pages=data.get('pages'),
            description=data.get('description'),
            location=data.get('location'),
            shelf_number=data.get('shelf_number'),
            purchase_date=datetime.strptime(data['purchase_date'], '%Y-%m-%d').date() if data.get('purchase_date') else None,
            purchase_price=data.get('purchase_price'),
            total_copies=data['total_copies'],
            copies_available=data['total_copies'],
            condition=data.get('condition', 'Good'),
            subject=data.get('subject'),
            reading_level=data.get('reading_level'),
            keywords=data.get('keywords', []),
            added_by_id=user.id
        )
        
        db.session.add(book)
        db.session.commit()
        
        return jsonify({
            'message': 'Book added successfully',
            'book': book.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@library_bp.route('/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book(book_id):
    """Get specific book details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        book = Book.query.get(book_id)
        if not book or book.school_id != user.school_id:
            return jsonify({'error': 'Book not found'}), 404
        
        # Get recent transactions for this book
        recent_transactions = LibraryTransaction.query.filter_by(
            book_id=book_id
        ).order_by(LibraryTransaction.transaction_date.desc()).limit(10).all()
        
        book_data = book.to_dict()
        book_data['recent_transactions'] = [t.to_dict() for t in recent_transactions]
        
        return jsonify({'book': book_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@library_bp.route('/books/<int:book_id>/borrow', methods=['POST'])
@jwt_required()
def borrow_book(book_id):
    """Borrow a book"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        book = Book.query.get(book_id)
        if not book or book.school_id != user.school_id:
            return jsonify({'error': 'Book not found'}), 404
        
        if book.copies_available <= 0:
            return jsonify({'error': 'Book not available'}), 400
        
        data = request.get_json()
        
        # Determine borrower
        if user.role in ['admin', 'teacher']:
            # Admin/teacher can issue book to any student/staff
            if not data.get('borrower_id') or not data.get('borrower_type'):
                return jsonify({'error': 'Borrower ID and type are required'}), 400
            
            borrower_id = data['borrower_id']
            borrower_type = data['borrower_type']  # student or staff
            
            if borrower_type == 'student':
                borrower = Student.query.get(borrower_id)
            else:
                borrower = Staff.query.get(borrower_id)
            
            if not borrower or borrower.school_id != user.school_id:
                return jsonify({'error': 'Borrower not found'}), 404
            
            borrower_user_id = borrower.user_id
        else:
            # Student/staff borrowing for themselves
            borrower_user_id = user.id
            borrower_type = 'student' if user.role == 'student' else 'staff'
            
            if borrower_type == 'student':
                borrower = Student.query.filter_by(user_id=user.id).first()
            else:
                borrower = Staff.query.filter_by(user_id=user.id).first()
            
            if not borrower:
                return jsonify({'error': 'Borrower profile not found'}), 404
            
            borrower_id = borrower.id
        
        # Check if user already has this book
        existing_transaction = LibraryTransaction.query.filter_by(
            book_id=book_id,
            borrower_user_id=borrower_user_id,
            transaction_type='borrow',
            status='active'
        ).first()
        
        if existing_transaction:
            return jsonify({'error': 'Book already borrowed by this user'}), 409
        
        # Calculate due date
        loan_period_days = book.loan_period_days or 14
        due_date = datetime.now().date() + timedelta(days=loan_period_days)
        
        # Create transaction
        transaction = LibraryTransaction(
            book_id=book_id,
            borrower_user_id=borrower_user_id,
            borrower_type=borrower_type,
            borrower_id=borrower_id,
            transaction_type='borrow',
            transaction_date=datetime.now().date(),
            due_date=due_date,
            issued_by_id=user.id,
            status='active'
        )
        
        # Update book availability
        book.copies_available -= 1
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Book borrowed successfully',
            'transaction': transaction.to_dict(),
            'due_date': due_date.isoformat()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@library_bp.route('/books/<int:book_id>/return', methods=['POST'])
@jwt_required()
def return_book(book_id):
    """Return a borrowed book"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        book = Book.query.get(book_id)
        if not book or book.school_id != user.school_id:
            return jsonify({'error': 'Book not found'}), 404
        
        data = request.get_json()
        
        # Find active borrowing transaction
        if user.role in ['admin', 'teacher'] and data.get('borrower_user_id'):
            borrower_user_id = data['borrower_user_id']
        else:
            borrower_user_id = user.id
        
        transaction = LibraryTransaction.query.filter_by(
            book_id=book_id,
            borrower_user_id=borrower_user_id,
            transaction_type='borrow',
            status='active'
        ).first()
        
        if not transaction:
            return jsonify({'error': 'No active borrowing transaction found'}), 404
        
        # Update transaction
        transaction.return_date = datetime.now().date()
        transaction.returned_to_id = user.id
        transaction.status = 'completed'
        transaction.condition_on_return = data.get('condition', 'Good')
        transaction.notes = data.get('notes')
        
        # Calculate fine if overdue
        if transaction.return_date > transaction.due_date:
            overdue_days = (transaction.return_date - transaction.due_date).days
            fine_per_day = book.fine_per_day or 5.0  # Default fine
            transaction.fine_amount = overdue_days * fine_per_day
        
        # Update book availability
        book.copies_available += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Book returned successfully',
            'transaction': transaction.to_dict(),
            'fine_amount': transaction.fine_amount or 0
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@library_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get library transactions"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        transaction_type = request.args.get('type')  # borrow, return
        status = request.args.get('status')  # active, completed, overdue
        borrower_id = request.args.get('borrower_id', type=int)
        
        # Build query
        query = LibraryTransaction.query.join(Book).filter(
            Book.school_id == user.school_id
        )
        
        # Filter by user role
        if user.role == 'student':
            query = query.filter(LibraryTransaction.borrower_user_id == user.id)
        elif user.role == 'teacher':
            # Teachers can see their own transactions and transactions they issued
            query = query.filter(
                db.or_(
                    LibraryTransaction.borrower_user_id == user.id,
                    LibraryTransaction.issued_by_id == user.id
                )
            )
        
        if transaction_type:
            query = query.filter(LibraryTransaction.transaction_type == transaction_type)
        
        if status:
            if status == 'overdue':
                query = query.filter(
                    LibraryTransaction.status == 'active',
                    LibraryTransaction.due_date < datetime.now().date()
                )
            else:
                query = query.filter(LibraryTransaction.status == status)
        
        if borrower_id:
            query = query.filter(LibraryTransaction.borrower_user_id == borrower_id)
        
        transactions = query.order_by(LibraryTransaction.transaction_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions.items],
            'pagination': {
                'total': transactions.total,
                'pages': transactions.pages,
                'current_page': page,
                'per_page': per_page
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@library_bp.route('/reservations', methods=['GET'])
@jwt_required()
def get_reservations():
    """Get book reservations"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Build query
        query = BookReservation.query.join(Book).filter(
            Book.school_id == user.school_id
        )
        
        # Filter by user role
        if user.role == 'student':
            query = query.filter(BookReservation.user_id == user.id)
        
        reservations = query.filter(BookReservation.status == 'active').order_by(
            BookReservation.reservation_date.desc()
        ).all()
        
        return jsonify({
            'reservations': [r.to_dict() for r in reservations],
            'total': len(reservations)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@library_bp.route('/books/<int:book_id>/reserve', methods=['POST'])
@jwt_required()
def reserve_book(book_id):
    """Reserve a book"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        book = Book.query.get(book_id)
        if not book or book.school_id != user.school_id:
            return jsonify({'error': 'Book not found'}), 404
        
        # Check if book is available
        if book.copies_available > 0:
            return jsonify({'error': 'Book is available for borrowing'}), 400
        
        # Check if user already has a reservation for this book
        existing = BookReservation.query.filter_by(
            book_id=book_id,
            user_id=user.id,
            status='active'
        ).first()
        
        if existing:
            return jsonify({'error': 'Book already reserved'}), 409
        
        reservation = BookReservation(
            book_id=book_id,
            user_id=user.id,
            reservation_date=datetime.now().date(),
            status='active'
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        return jsonify({
            'message': 'Book reserved successfully',
            'reservation': reservation.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@library_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_library_analytics():
    """Get library analytics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Basic statistics
        total_books = Book.query.filter_by(school_id=user.school_id, is_active=True).count()
        total_copies = db.session.query(db.func.sum(Book.total_copies)).filter_by(
            school_id=user.school_id, is_active=True
        ).scalar() or 0
        
        available_copies = db.session.query(db.func.sum(Book.copies_available)).filter_by(
            school_id=user.school_id, is_active=True
        ).scalar() or 0
        
        borrowed_copies = total_copies - available_copies
        
        # Active transactions
        active_borrowings = LibraryTransaction.query.join(Book).filter(
            Book.school_id == user.school_id,
            LibraryTransaction.status == 'active'
        ).count()
        
        # Overdue books
        overdue_books = LibraryTransaction.query.join(Book).filter(
            Book.school_id == user.school_id,
            LibraryTransaction.status == 'active',
            LibraryTransaction.due_date < datetime.now().date()
        ).count()
        
        # Popular books (most borrowed)
        from sqlalchemy import func
        popular_books = db.session.query(
            Book.title,
            func.count(LibraryTransaction.id).label('borrow_count')
        ).join(LibraryTransaction).filter(
            Book.school_id == user.school_id
        ).group_by(Book.id, Book.title).order_by(
            func.count(LibraryTransaction.id).desc()
        ).limit(10).all()
        
        # Category-wise distribution
        category_stats = db.session.query(
            BookCategory.name,
            func.count(Book.id).label('book_count')
        ).join(Book).filter(
            Book.school_id == user.school_id,
            Book.is_active == True
        ).group_by(BookCategory.id, BookCategory.name).all()
        
        analytics = {
            'overview': {
                'total_books': total_books,
                'total_copies': total_copies,
                'available_copies': available_copies,
                'borrowed_copies': borrowed_copies,
                'utilization_rate': round((borrowed_copies / total_copies * 100), 2) if total_copies > 0 else 0,
                'active_borrowings': active_borrowings,
                'overdue_books': overdue_books
            },
            'popular_books': [
                {'title': book.title, 'borrow_count': book.borrow_count}
                for book in popular_books
            ],
            'category_distribution': [
                {'category': cat.name, 'book_count': cat.book_count}
                for cat in category_stats
            ]
        }
        
        return jsonify({'analytics': analytics})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500