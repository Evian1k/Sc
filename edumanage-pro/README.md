# EduManage Pro - School Management System

A comprehensive full-stack school management system built with Flask (backend) and React (frontend). This system provides complete functionality for managing students, staff, attendance, grades, and fees.

## 🌟 Features

### Core Functionality
- **Student Management**: Add, edit, view, and manage student records
- **Staff Management**: Manage teachers, administrators, and support staff
- **Attendance Tracking**: Check-in/check-out system with bulk attendance marking
- **Grading System**: Complete grade management with automatic GPA calculation
- **Fee Management**: Track tuition, library, lab, and other fees with payment recording
- **Role-based Access**: Admin, Teacher, and Student roles with appropriate permissions

### Technical Features
- **Authentication**: JWT-based secure authentication
- **RESTful API**: Complete REST API with proper error handling
- **Responsive Design**: Modern, mobile-friendly interface built with Tailwind CSS
- **Real-time Updates**: Dynamic dashboard with live statistics
- **Data Validation**: Comprehensive input validation and error handling
- **Database Seeding**: Pre-populated sample data for testing

## 🛠 Technology Stack

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM
- **Flask-JWT-Extended**: JWT authentication
- **Flask-CORS**: Cross-origin resource sharing
- **SQLite**: Database (easily configurable for PostgreSQL/MySQL)

### Frontend
- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **Heroicons**: Beautiful SVG icons

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd edumanage-pro
   ```

2. **Run the complete system** (Recommended)
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
   This will start both backend and frontend servers automatically.

3. **Or run servers separately:**

   **Backend Setup:**
   ```bash
   chmod +x run-backend.sh
   ./run-backend.sh
   ```

   **Frontend Setup:** (In a new terminal)
   ```bash
   chmod +x run-frontend.sh
   ./run-frontend.sh
   ```

### Manual Setup (Alternative)

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py  # Optional: Add sample data
python run.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🔗 Access URLs

- **Frontend Application**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api (when running)

## 👤 Default Login Credentials

The system comes with pre-seeded users for testing:

| Role | Username | Password | Description |
|------|----------|----------|-------------|
| Admin | `admin` | `admin123` | Full system access |
| Teacher | `john_teacher` | `teacher123` | Teacher access |
| Student | `alice_student` | `student123` | Student access |

## 📊 Database Schema

### Core Models
- **User**: Authentication and base user information
- **Student**: Student profiles with academic information
- **Staff**: Staff profiles with employment details
- **Class**: Class/grade organization
- **Subject**: Academic subjects
- **Attendance**: Daily attendance records
- **Grade**: Academic grades and assessments
- **Fee**: Fee structure and payment tracking

## 🗂 Project Structure

```
edumanage-pro/
├── backend/                 # Flask backend
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   └── __init__.py     # App factory
│   ├── config.py           # Configuration
│   ├── requirements.txt    # Python dependencies
│   ├── seed.py            # Database seeding
│   └── run.py             # Application runner
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── contexts/      # React contexts
│   │   ├── services/      # API services
│   │   └── utils/         # Utility functions
│   ├── public/            # Static assets
│   └── package.json       # Node dependencies
├── start.sh              # Start both servers
├── run-backend.sh        # Backend runner script
├── run-frontend.sh       # Frontend runner script
└── README.md            # This file
```

## 📚 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `POST /api/auth/change-password` - Change password

### Students
- `GET /api/students` - List students (with pagination)
- `POST /api/students` - Create new student
- `GET /api/students/{id}` - Get student details
- `PUT /api/students/{id}` - Update student
- `DELETE /api/students/{id}` - Delete student

### Staff
- `GET /api/staff` - List staff members
- `POST /api/staff` - Create new staff member
- `GET /api/staff/{id}` - Get staff details
- `PUT /api/staff/{id}` - Update staff member

### Attendance
- `GET /api/attendance` - Get attendance records
- `POST /api/attendance/check-in` - Mark student check-in
- `POST /api/attendance/bulk-mark` - Bulk attendance marking
- `GET /api/attendance/report` - Attendance reports

### Grades
- `GET /api/grades` - List grades
- `POST /api/grades` - Add new grade
- `GET /api/grades/student/{id}/report` - Student grade report
- `GET /api/grades/subjects` - List subjects

### Fees
- `GET /api/fees` - List fee records
- `POST /api/fees` - Create fee record
- `POST /api/fees/{id}/payment` - Record payment
- `GET /api/fees/student/{id}/summary` - Student fee summary

## 🎨 Features by User Role

### Admin Dashboard
- System-wide statistics
- Student and staff management
- Fee collection reports
- System configuration

### Teacher Dashboard
- Class attendance marking
- Grade entry and management
- Student performance reports
- Class-specific analytics

### Student Dashboard
- Personal attendance history
- Grade reports and GPA
- Fee payment status
- Academic progress tracking

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///edumanage.db
```

### Frontend Configuration
The frontend automatically proxies API requests to the backend. Update `vite.config.js` if needed:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
      secure: false,
    },
  },
}
```

## 📈 Sample Data

The system includes comprehensive sample data:
- 6 classes (Grade 1A, 1B, 2A, 3A, 4A, 5A)
- 15 students across different grades
- 4 teachers + 1 admin
- 7 subjects (Math, English, Science, etc.)
- 30 days of attendance history
- Grade records for multiple assessments
- Fee records with various payment statuses

## 🚀 Production Deployment

### Backend (Flask)
1. Use a production WSGI server (e.g., Gunicorn)
2. Configure a production database (PostgreSQL recommended)
3. Set up proper environment variables
4. Configure reverse proxy (Nginx)

### Frontend (React)
1. Build the production bundle: `npm run build`
2. Serve static files with a web server
3. Configure proper routing for SPA

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔮 Future Enhancements

- **Timetable Management**: Class scheduling and timetable generation
- **Communication System**: Messages between teachers, students, and parents
- **Library Management**: Book inventory and borrowing system
- **Transportation**: Bus route management and tracking
- **Exam Management**: Comprehensive exam scheduling and management
- **Reports**: Advanced reporting and analytics
- **Mobile App**: React Native mobile application
- **Notifications**: Email and SMS notifications
- **Document Management**: File uploads and document storage

## 📞 Support

For support, please create an issue in the repository or contact the development team.

---

**EduManage Pro** - Making school management simple and efficient! 🎓