#!/usr/bin/env python3
"""
Run script for EduManage Pro Backend
"""

import os
import sys
from app import create_app, db

def main():
    app = create_app()
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        print("Database tables created/verified.")
    
    print("Starting EduManage Pro Backend...")
    print("API will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()