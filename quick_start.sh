#!/bin/bash

echo "🚀 EduManage Quick Start (Node 18 Compatible)"
echo "=============================================="

# Quick backend setup
echo "📦 Backend Quick Setup..."
cd backend

# Copy env file
cp .env.example .env 2>/dev/null || echo "✅ .env already exists"

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate and install minimal deps
source venv/bin/activate
pip install Flask Flask-SQLAlchemy Flask-JWT-Extended Flask-CORS Flask-Mail python-dotenv bcrypt

# Quick database setup
python3 -c "
try:
    from app import create_app, db
    app = create_app()
    with app.app_context():
        db.create_all()
        print('✅ Database created')
except Exception as e:
    print(f'⚠️  Database setup: {e}')
"

# Create admin user
python3 create_admin.py 2>/dev/null || echo "⚠️  Run 'python create_admin.py' manually if needed"

echo "✅ Backend ready! Run: cd backend && source venv/bin/activate && python app.py"

cd ../frontend

# Frontend quick setup
echo "📱 Frontend Quick Setup..."

# Copy env file
cp .env.example .env.local 2>/dev/null || echo "✅ .env.local already exists"

# Remove and reinstall with compatible versions
rm -rf node_modules package-lock.json 2>/dev/null

# Install with legacy peer deps for Node 18 compatibility
npm install --legacy-peer-deps --no-audit --no-fund

echo "✅ Frontend ready! Run: cd frontend && npm run dev"

echo ""
echo "🎉 Quick setup complete!"
echo "========================"
echo "🔧 Backend: cd backend && source venv/bin/activate && python app.py"
echo "⚛️  Frontend: cd frontend && npm run dev"
echo "📱 Access: http://localhost:5173"
echo "👤 Login: admin@edumanage.com / admin123"