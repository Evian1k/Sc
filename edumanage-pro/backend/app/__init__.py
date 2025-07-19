from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.students import students_bp
    from app.routes.staff import staff_bp
    from app.routes.attendance import attendance_bp
    from app.routes.grades import grades_bp
    from app.routes.fees import fees_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(grades_bp, url_prefix='/api/grades')
    app.register_blueprint(fees_bp, url_prefix='/api/fees')
    
    return app