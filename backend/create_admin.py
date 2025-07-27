#!/usr/bin/env python3
"""
Script to create a default admin user for EduManage
Run this after setting up the database to create the initial admin account
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, School, Staff

def create_default_admin():
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@edumanage.com').first()
        if admin_user:
            print("Admin user already exists!")
            print(f"Email: admin@edumanage.com")
            print("You can change the password through the settings.")
            return
        
        # Get or create default school
        school = School.query.first()
        if not school:
            school = School(
                name="EduManage Demo School",
                short_name="EDS",
                code="EDS001",
                email="admin@edumanage-demo.com",
                phone="+254700000000",
                address="123 Education Street",
                city="Nairobi",
                country="Kenya"
            )
            db.session.add(school)
            db.session.flush()  # Get the school ID
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@edumanage.com',
            first_name='System',
            last_name='Administrator',
            phone_number='+254700000000',
            role='admin',
            school_id=school.id,
            is_verified=True,
            is_active=True
        )
        admin_user.set_password('admin123')  # Default password
        
        db.session.add(admin_user)
        db.session.flush()  # Get the user ID
        
        # Create staff profile for admin
        admin_staff = Staff(
            user_id=admin_user.id,
            school_id=school.id,
            employee_id='EMP001',
            position='Administrator',
            department='Administration',
            date_of_joining=db.func.current_date(),
            salary=0.0,  # Will be set later
            is_active=True
        )
        
        db.session.add(admin_staff)
        db.session.commit()
        
        print("✅ Default admin user created successfully!")
        print("=" * 50)
        print("📧 Email: admin@edumanage.com")
        print("🔑 Password: admin123")
        print("🏫 School: EduManage Demo School")
        print("=" * 50)
        print("⚠️  Please change the default password after first login!")
        print("🔗 Login at: http://localhost:5173")

if __name__ == '__main__':
    create_default_admin()