# EduManage Ultimate School Management System

A comprehensive, professional-grade school management system built with React (frontend) and Flask (backend).

## 🌟 Features

### 📚 Academic Management
- **Student Management**: Complete student profiles, enrollment, and academic tracking
- **Staff Management**: Teacher and staff profiles with role-based access
- **Class Management**: Class creation, subject assignment, and timetable management
- **Grade Management**: Grade entry, performance analytics, and report cards
- **Exam Management**: Exam scheduling, result entry, and performance analysis

### 💰 Financial Management
- **Fee Management**: Fee structure setup, payment tracking, and balance monitoring
- **Payment Processing**: Payment recording and receipt generation
- **Financial Reports**: Revenue tracking and collection analytics

### 📅 Attendance & Monitoring
- **Daily Attendance**: Manual attendance marking with multiple status options
- **QR Code Attendance**: Generate and scan QR codes for quick attendance
- **Attendance Analytics**: Real-time attendance rates and patterns
- **Parent Notifications**: Automatic SMS/email alerts for attendance

### 👨‍👩‍👧‍👦 Parent Portal
- **Multi-child Management**: Parents can monitor multiple children
- **Academic Progress**: View grades, attendance, and performance
- **Fee Tracking**: Monitor fee payments and outstanding balances
- **Communication**: Receive school notifications and updates

### 📊 Analytics & Reporting
- **Performance Analytics**: Class and subject performance insights
- **Financial Analytics**: Fee collection and revenue analysis
- **Attendance Reports**: Detailed attendance statistics
- **Custom Reports**: Generate various PDF reports

### 🔧 Administrative Features
- **Multi-tenant Architecture**: Support for multiple schools
- **Role-based Access Control**: Admin, Teacher, Student, Parent, Accountant roles
- **School Settings**: Customizable school configuration
- **User Management**: Complete user account management

## 🚀 Quick Start

### Prerequisites
- **Backend**: Python 3.8+, PostgreSQL (or SQLite for development)
- **Frontend**: Node.js 16+, npm or yarn

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
cp .env.example .env
# Edit .env with your database and configuration settings

# Initialize database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Create default admin user
python create_admin.py

# Run the backend server
python app.py
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local
# Edit .env.local if needed (default API URL is already set)

# Start development server
npm run dev
```

### 3. Access the System

1. **Frontend**: http://localhost:5173
2. **Backend API**: http://localhost:5000
3. **Default Login**:
   - **Email**: admin@edumanage.com
   - **Password**: admin123

## 🔧 Configuration

### Backend Configuration (.env)
```env
# Database
DATABASE_URL=sqlite:///edumanage.db
# For PostgreSQL: postgresql://username:password@localhost/edumanage

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Email Settings (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# SMS Settings (optional)
AFRICASTALKING_USERNAME=your-username
AFRICASTALKING_API_KEY=your-api-key

# Features
ENABLE_SMS_NOTIFICATIONS=False
ENABLE_EMAIL_NOTIFICATIONS=False
ENABLE_QR_ATTENDANCE=True
MULTI_TENANT_MODE=False
```

### Frontend Configuration (.env.local)
```env
VITE_API_URL=http://localhost:5000/api
```

## 📱 User Roles & Access

### 🔑 Admin
- Complete system access
- User management
- School settings
- Financial oversight
- Analytics and reports

### 👨‍🏫 Teacher
- Class management
- Grade entry
- Attendance marking
- Student progress monitoring

### 🎓 Student
- View grades and attendance
- Access academic records
- Download report cards

### 👨‍👩‍👧‍👦 Parent
- Monitor children's progress
- View attendance and grades
- Track fee payments
- Receive notifications

### 💼 Accountant
- Fee management
- Payment processing
- Financial reporting

## 🏗️ Architecture

### Backend (Flask)
- **API**: RESTful API with JWT authentication
- **Database**: SQLAlchemy ORM with PostgreSQL/SQLite
- **Security**: Role-based access control, input validation
- **Services**: Modular service layer for business logic

### Frontend (React)
- **UI Framework**: React 18 with modern hooks
- **Styling**: Tailwind CSS for responsive design
- **State Management**: Context API for authentication
- **Routing**: React Router for navigation

### Key Technologies
- **Backend**: Flask, SQLAlchemy, JWT, Celery, Redis
- **Frontend**: React, Tailwind CSS, Axios, React Router
- **Database**: PostgreSQL (production), SQLite (development)
- **Additional**: QR code generation, PDF reports, SMS/Email integration

## 📁 Project Structure

```
edumanage/
├── backend/                    # Flask backend
│   ├── app/
│   │   ├── models/            # Database models
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   └── __init__.py        # App factory
│   ├── config.py              # Configuration
│   ├── app.py                 # Application entry point
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── contexts/          # React contexts
│   │   ├── services/          # API services
│   │   └── App.jsx            # Main app component
│   ├── package.json           # Node dependencies
│   └── vite.config.js         # Vite configuration
└── README.md                  # This file
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `POST /api/auth/change-password` - Change password

### Students
- `GET /api/students` - List students
- `POST /api/students` - Create student
- `PUT /api/students/{id}` - Update student
- `DELETE /api/students/{id}` - Delete student

### Staff
- `GET /api/staff` - List staff
- `POST /api/staff` - Create staff member
- `PUT /api/staff/{id}` - Update staff
- `DELETE /api/staff/{id}` - Delete staff

### Classes & Subjects
- `GET /api/classes` - List classes
- `POST /api/classes` - Create class
- `GET /api/classes/subjects` - List subjects
- `POST /api/classes/subjects` - Create subject

### Attendance
- `GET /api/attendance` - Get attendance records
- `POST /api/attendance/mark` - Mark attendance
- `GET /api/attendance/analytics` - Attendance analytics

### Grades
- `GET /api/grades` - Get grades
- `POST /api/grades` - Add grade
- `GET /api/grades/analytics` - Grade analytics

### Fees
- `GET /api/fees` - List fees
- `POST /api/fees` - Create fee
- `POST /api/fees/{id}/payment` - Record payment

### And many more...

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📦 Deployment

### Production Backend
1. Set up PostgreSQL database
2. Configure production environment variables
3. Run database migrations
4. Deploy with Gunicorn + Nginx

### Production Frontend
1. Build the application: `npm run build`
2. Deploy to static hosting (Netlify, Vercel, etc.)
3. Configure API URL for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, email support@edumanage.com or create an issue in the GitHub repository.

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Integration with external services
- [ ] Multi-language support
- [ ] Advanced reporting features
- [ ] Biometric attendance integration

---

**Made with ❤️ for education management**