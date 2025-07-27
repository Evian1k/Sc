#!/bin/bash

echo "🔧 EduManage Setup Fix Script"
echo "============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Please run this script from the root directory (where backend/ and frontend/ folders are)"
    exit 1
fi

print_status "Starting EduManage setup fix..."

# Backend setup
echo ""
echo "🐍 Fixing Backend Setup..."
cd backend

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from example..."
    cp .env.example .env
    print_warning "Please edit .env file with your settings if needed"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install minimal requirements first
print_status "Installing core Python dependencies..."
pip install --upgrade pip
pip install -r requirements-minimal.txt

# Test if basic imports work
print_status "Testing basic imports..."
python3 -c "from flask import Flask; print('Flask import successful')" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "Core dependencies installed successfully"
else
    print_error "Failed to install core dependencies"
    exit 1
fi

# Install remaining dependencies
print_status "Installing remaining Python dependencies..."
pip install -r requirements.txt

# Create database
print_status "Setting up database..."
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database created successfully')"

# Create admin user
print_status "Creating admin user..."
python3 create_admin.py

cd ..

# Frontend setup
echo ""
echo "⚛️  Fixing Frontend Setup..."
cd frontend

# Create .env.local file if it doesn't exist
if [ ! -f ".env.local" ]; then
    print_status "Creating .env.local file from example..."
    cp .env.example .env.local
fi

# Remove problematic node_modules and package-lock.json
if [ -d "node_modules" ]; then
    print_status "Removing old node_modules..."
    rm -rf node_modules
fi

if [ -f "package-lock.json" ]; then
    print_status "Removing old package-lock.json..."
    rm -f package-lock.json
fi

# Clear npm cache
print_status "Clearing npm cache..."
npm cache clean --force

# Install dependencies with legacy peer deps flag
print_status "Installing Node.js dependencies (Node 18 compatible)..."
npm install --legacy-peer-deps

# Verify installation
if [ -d "node_modules" ]; then
    print_status "Frontend dependencies installed successfully"
else
    print_error "Failed to install frontend dependencies"
    exit 1
fi

cd ..

# Final verification
echo ""
echo "🧪 Running Final Verification..."

# Test backend
cd backend
source venv/bin/activate
print_status "Testing backend imports..."
python3 -c "from app import create_app; print('✅ Backend ready')" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "Backend is ready to run"
else
    print_error "Backend still has issues"
fi
cd ..

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📱 To start the application:"
echo "1. Backend: cd backend && source venv/bin/activate && python app.py"
echo "2. Frontend: cd frontend && npm run dev"
echo ""
echo "🔗 Access URLs:"
echo "• Frontend: http://localhost:5173"
echo "• Backend: http://localhost:5000"
echo ""
echo "👤 Default Login:"
echo "• Email: admin@edumanage.com"
echo "• Password: admin123"
echo ""
print_status "All issues should now be fixed!"