import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///edumanage.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # SMS Configuration - Twilio
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # SMS Configuration - Africa's Talking
    AFRICASTALKING_USERNAME = os.environ.get('AFRICASTALKING_USERNAME')
    AFRICASTALKING_API_KEY = os.environ.get('AFRICASTALKING_API_KEY')
    AFRICASTALKING_SENDER_ID = os.environ.get('AFRICASTALKING_SENDER_ID')
    
    # WhatsApp Configuration
    WHATSAPP_API_URL = os.environ.get('WHATSAPP_API_URL')
    WHATSAPP_API_TOKEN = os.environ.get('WHATSAPP_API_TOKEN')
    
    # Redis Configuration (for Celery and caching)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or REDIS_URL
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or REDIS_URL
    
    # Multi-tenancy Configuration
    MULTI_TENANT_MODE = os.environ.get('MULTI_TENANT_MODE', 'false').lower() in ['true', 'on', '1']
    DEFAULT_SCHOOL_DOMAIN = os.environ.get('DEFAULT_SCHOOL_DOMAIN') or 'localhost'
    
    # Security Configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "100 per minute"
    
    # Pagination
    STUDENTS_PER_PAGE = 20
    STAFF_PER_PAGE = 20
    GRADES_PER_PAGE = 50
    ATTENDANCE_PER_PAGE = 100
    
    # Feature Flags
    ENABLE_SMS_NOTIFICATIONS = os.environ.get('ENABLE_SMS_NOTIFICATIONS', 'true').lower() in ['true', 'on', '1']
    ENABLE_EMAIL_NOTIFICATIONS = os.environ.get('ENABLE_EMAIL_NOTIFICATIONS', 'true').lower() in ['true', 'on', '1']
    ENABLE_WHATSAPP_NOTIFICATIONS = os.environ.get('ENABLE_WHATSAPP_NOTIFICATIONS', 'false').lower() in ['true', 'on', '1']
    ENABLE_BIOMETRIC_ATTENDANCE = os.environ.get('ENABLE_BIOMETRIC_ATTENDANCE', 'false').lower() in ['true', 'on', '1']
    ENABLE_QR_ATTENDANCE = os.environ.get('ENABLE_QR_ATTENDANCE', 'true').lower() in ['true', 'on', '1']
    
    # Academic Configuration
    ACADEMIC_YEAR_START_MONTH = int(os.environ.get('ACADEMIC_YEAR_START_MONTH') or 9)  # September
    GRADE_SCALE = os.environ.get('GRADE_SCALE') or 'A-F'  # A-F, 1-100, etc.
    PASSING_GRADE = float(os.environ.get('PASSING_GRADE') or 50.0)
    
    # Backup Configuration
    BACKUP_SCHEDULE = os.environ.get('BACKUP_SCHEDULE') or '0 2 * * *'  # Daily at 2 AM
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS') or 30)
    
    # Analytics and Reporting
    ENABLE_ANALYTICS = os.environ.get('ENABLE_ANALYTICS', 'true').lower() in ['true', 'on', '1']
    ANALYTICS_RETENTION_MONTHS = int(os.environ.get('ANALYTICS_RETENTION_MONTHS') or 24)
    
    # API Configuration
    API_VERSION = 'v1'
    API_TITLE = 'EduManage Ultimate School Management System API'
    API_DESCRIPTION = 'Comprehensive school management system with multi-role support'
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///edumanage_dev.db'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///edumanage_test.db'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:pass@localhost/edumanage'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}