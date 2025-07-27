#!/bin/bash

echo "🚀 Starting EduManage Development Environment"
echo "=============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo "✅ Python and Node.js are installed."

# Function to start backend
start_backend() {
    echo "📦 Setting up backend..."
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "🔧 Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create database and admin user
    echo "🗄️ Setting up database..."
    python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
    
    # Create admin user
    echo "👤 Creating admin user..."
    python create_admin.py
    
    # Start backend server
    echo "🚀 Starting backend server on http://localhost:5000..."
    python app.py &
    BACKEND_PID=$!
    cd ..
    return $BACKEND_PID
}

# Function to start frontend
start_frontend() {
    echo "⚛️ Setting up frontend..."
    cd frontend
    
    # Install dependencies
    echo "📥 Installing Node dependencies..."
    npm install
    
    # Start frontend server
    echo "🚀 Starting frontend server on http://localhost:5173..."
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    return $FRONTEND_PID
}

# Start both servers
echo ""
echo "Starting backend server..."
start_backend
BACKEND_PID=$!

sleep 3

echo ""
echo "Starting frontend server..."
start_frontend
FRONTEND_PID=$!

# Display information
echo ""
echo "🎉 EduManage is starting up!"
echo "================================"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:5000"
echo "👤 Default Login:"
echo "   📧 Email: admin@edumanage.com"
echo "   🔑 Password: admin123"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to handle shutdown
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped. Goodbye!"
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait