#!/bin/bash

echo "🔧 Fixing Node.js compatibility issues..."

# Navigate to frontend directory
cd frontend

echo "📦 Removing node_modules and package-lock.json..."
rm -rf node_modules package-lock.json

echo "📋 Installing compatible dependencies..."
npm install

echo "✅ Node.js compatibility issues fixed!"
echo ""
echo "📚 To run the frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "🌐 The frontend will be available at: http://localhost:5173"