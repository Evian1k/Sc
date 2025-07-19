#!/bin/bash

echo "=========================================="
echo "EduManage Pro - Initial Setup"
echo "=========================================="

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi
echo "✅ npm found: $(npm --version)"

echo ""
echo "Setting up backend..."

# Backend setup
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setting up database and seeding data..."
python seed.py

cd ..

echo ""
echo "Setting up frontend..."

# Frontend setup
cd frontend
echo "Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "Making scripts executable..."
chmod +x *.sh

echo ""
echo "=========================================="
echo "✅ Setup completed successfully!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  ./start.sh        - Start both backend and frontend"
echo "  ./run-backend.sh  - Start only backend"
echo "  ./run-frontend.sh - Start only frontend"
echo ""
echo "Default login credentials:"
echo "  Admin:   username=admin,        password=admin123"
echo "  Teacher: username=john_teacher, password=teacher123" 
echo "  Student: username=alice_student, password=student123"
echo ""
echo "Access URLs:"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:5000"
echo "=========================================="