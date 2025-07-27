from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Book, BookCategory, LibraryTransaction
from datetime import datetime, timedelta

library_bp = Blueprint('library', __name__)

@library_bp.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    """Get all books in the library"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        books = Book.query.filter_by(school_id=user.school_id).all()

        return jsonify({
            'books': [book.to_dict() for book in books],
            'total': len(books)
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

        book = Book(
            school_id=user.school_id,
            title=data.get('title'),
            author=data.get('author'),
            isbn=data.get('isbn'),
            category_id=data.get('category_id'),
            total_copies=data.get('total_copies', 1),
            available_copies=data.get('total_copies', 1),
            publisher=data.get('publisher'),
            publication_year=data.get('publication_year'),
            description=data.get('description'),
            location=data.get('location'),
            created_by_id=user.id
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

@library_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all book categories"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        categories = BookCategory.query.filter_by(school_id=user.school_id).all()

        return jsonify({
            'categories': [cat.to_dict() for cat in categories],
            'total': len(categories)
        })

    except Exception as e:
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

        transactions = LibraryTransaction.query.join(Book).filter(
            Book.school_id == user.school_id
        ).order_by(LibraryTransaction.borrowed_date.desc()).all()

        return jsonify({
            'transactions': [trans.to_dict() for trans in transactions],
            'total': len(transactions)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@library_bp.route('/borrow', methods=['POST'])
@jwt_required()
def borrow_book():
    """Borrow a book"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        book_id = data.get('book_id')
        student_id = data.get('student_id')

        book = Book.query.get(book_id)
        if not book or book.school_id != user.school_id:
            return jsonify({'error': 'Book not found'}), 404

        if book.available_copies <= 0:
            return jsonify({'error': 'Book not available'}), 400

        # Create transaction
        transaction = LibraryTransaction(
            book_id=book_id,
            student_id=student_id,
            borrowed_date=datetime.utcnow().date(),
            due_date=(datetime.utcnow() + timedelta(days=14)).date(),
            status='borrowed',
            issued_by_id=user.id
        )

        # Update book availability
        book.available_copies -= 1

        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            'message': 'Book borrowed successfully',
            'transaction': transaction.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500