#!/bin/bash

echo "Starting EduManage Pro - Full Stack School Management System"
echo "============================================================="

# Function to cleanup background processes
cleanup() {
    echo "Shutting down servers..."
    kill $(jobs -p) 2>/dev/null
    exit
}

# Trap SIGINT and SIGTERM to cleanup
trap cleanup SIGINT SIGTERM

# Make scripts executable
chmod +x run-backend.sh
chmod +x run-frontend.sh

echo "Starting backend server in background..."
./run-backend.sh &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 5

echo "Starting frontend server..."
./run-frontend.sh &
FRONTEND_PID=$!

echo ""
echo "============================================================="
echo "EduManage Pro is starting up..."
echo "Backend API: http://localhost:5000"
echo "Frontend App: http://localhost:5173"
echo "============================================================="
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID