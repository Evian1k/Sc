# 🚀 EduManage Pro - Quick Start Guide

## One-Command Setup & Run

```bash
# Clone the repository
git clone https://github.com/Evian1k/Sc.git
cd Sc

# Setup everything (installs dependencies, creates database, seeds data)
./setup.sh

# Start both backend and frontend
./start.sh
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

---

**Need help?** Check the main [README.md](README.md) for detailed documentation.