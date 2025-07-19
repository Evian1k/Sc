# 🚀 EduManage Pro - Quick Start Guide

## Prerequisites
- **Python 3.8+**
- **Node.js 18.0.0+** (tested with 18.19.1)
- **npm 8.0.0+**

## One-Command Setup & Run

```bash
# Clone the repository
git clone https://github.com/Evian1k/Sc.git
cd Sc

# Quick fix for Node.js version issues (if needed)
./fix-node-issues.sh

# Setup everything (installs dependencies, creates database, seeds data)
./setup.sh

# Start both backend and frontend
./start.sh
```

## 🚨 Fix Node.js Version Issues

If you see errors like:
```
npm WARN EBADENGINE Unsupported engine
TypeError: crypto.hash is not a function
```

**Quick Fix:**
```bash
./fix-node-issues.sh
```

## Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000

## Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Teacher | `john_teacher` | `teacher123` |
| Student | `alice_student` | `student123` |

## What's Included

✅ **Complete Backend** (Flask)
- Authentication with JWT
- Student management
- Staff management  
- Attendance tracking
- Grades management
- Fee management
- Database with sample data

✅ **Modern Frontend** (React + Vite)
- Role-based dashboards
- Responsive design with Tailwind CSS
- Complete UI for all features
- Real-time updates

✅ **Ready to Use**
- Pre-configured proxy
- Sample data included
- All dependencies defined
- Easy setup scripts
- Node.js compatibility fixes

## Manual Setup (Alternative)

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed.py
python run.py
```

**Frontend:**
```bash
cd frontend
rm -rf node_modules package-lock.json  # Clear any version conflicts
npm install
npm run dev
```

## Features

- 👥 **Student Management**: CRUD operations, class assignment
- 👨‍🏫 **Staff Management**: Teachers, admin roles
- 📊 **Attendance**: Check-in/out, bulk marking, reports
- 📝 **Grades**: Assessment tracking, GPA calculation
- 💰 **Fees**: Payment tracking, status management
- 🔐 **Authentication**: Role-based access control
- 📱 **Responsive**: Works on desktop and mobile

## Troubleshooting

**Node.js 20+ Issues**: This project is optimized for Node.js 18.x due to compatibility issues with newer Vite versions.

**Port Conflicts**: If ports 5000 or 5173 are busy:
```bash
sudo lsof -t -i:5000 | xargs kill -9
sudo lsof -t -i:5173 | xargs kill -9
```

---

**Need help?** Check the main [README.md](README.md) for detailed documentation.