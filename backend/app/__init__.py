from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    limiter.init_app(app)
    CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])
    
    # Create upload directory if it doesn't exist
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Register blueprints - existing routes
    from app.routes.auth import auth_bp
    from app.routes.students import students_bp
    from app.routes.staff import staff_bp
    from app.routes.attendance import attendance_bp
    from app.routes.grades import grades_bp
    from app.routes.fees import fees_bp
    
    # Register new comprehensive routes
    from app.routes.schools import schools_bp
    from app.routes.parents import parents_bp
    from app.routes.exams import exams_bp
    from app.routes.library import library_bp
    from app.routes.events import events_bp
    from app.routes.messages import messages_bp
    from app.routes.timetables import timetables_bp
    from app.routes.reports import reports_bp
    from app.routes.notifications import notifications_bp
    from app.routes.qr_codes import qr_bp
    from app.routes.analytics import analytics_bp
    from app.routes.admin import admin_bp
    
    # Register all blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(grades_bp, url_prefix='/api/grades')
    app.register_blueprint(fees_bp, url_prefix='/api/fees')
    
    # New comprehensive routes
    app.register_blueprint(schools_bp, url_prefix='/api/schools')
    app.register_blueprint(parents_bp, url_prefix='/api/parents')
    app.register_blueprint(exams_bp, url_prefix='/api/exams')
    app.register_blueprint(library_bp, url_prefix='/api/library')
    app.register_blueprint(events_bp, url_prefix='/api/events')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    app.register_blueprint(timetables_bp, url_prefix='/api/timetables')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(qr_bp, url_prefix='/api/qr')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {'error': 'Rate limit exceeded', 'message': str(e.description)}, 429
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'timestamp': db.func.now(),
            'version': '1.0.0',
            'features': {
                'sms_notifications': app.config.get('ENABLE_SMS_NOTIFICATIONS', False),
                'email_notifications': app.config.get('ENABLE_EMAIL_NOTIFICATIONS', False),
                'qr_attendance': app.config.get('ENABLE_QR_ATTENDANCE', False),
                'biometric_attendance': app.config.get('ENABLE_BIOMETRIC_ATTENDANCE', False),
                'multi_tenant': app.config.get('MULTI_TENANT_MODE', False)
            }
        }
    
    # API documentation endpoint
    @app.route('/api')
    def api_info():
        return {
            'title': app.config.get('API_TITLE', 'EduManage API'),
            'description': app.config.get('API_DESCRIPTION', 'School Management System API'),
            'version': app.config.get('API_VERSION', 'v1'),
            'endpoints': {
                'authentication': '/api/auth',
                'students': '/api/students',
                'staff': '/api/staff',
                'parents': '/api/parents',
                'attendance': '/api/attendance',
                'grades': '/api/grades',
                'exams': '/api/exams',
                'fees': '/api/fees',
                'library': '/api/library',
                'events': '/api/events',
                'messages': '/api/messages',
                'timetables': '/api/timetables',
                'reports': '/api/reports',
                'notifications': '/api/notifications',
                'qr_codes': '/api/qr',
                'analytics': '/api/analytics',
                'administration': '/api/admin'
            }
        }
    
    # Initialize database tables and default data
    with app.app_context():
        # Import all models to ensure they're registered
        from app.models import *
        
        # Create tables
        db.create_all()
        
        # Create default school if none exists and not in multi-tenant mode
        if not app.config.get('MULTI_TENANT_MODE', False):
            from app.models import School
            default_school = School.query.first()
            if not default_school:
                default_school = School(
                    name="EduManage Demo School",
                    short_name="EDS",
                    code="EDS001",
                    email="admin@edumanage-demo.com",
                    phone="+254700000000",
                    address="123 Education Street",
                    city="Nairobi",
                    country="Kenya"
                )
                db.session.add(default_school)
                db.session.commit()
    
    return app

# Import models to make them available
from app import models