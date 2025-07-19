import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getProfile: () => api.get('/auth/profile'),
  changePassword: (passwords) => api.post('/auth/change-password', passwords),
};

// Students API
export const studentsAPI = {
  getAll: (params) => api.get('/students', { params }),
  getById: (id) => api.get(`/students/${id}`),
  create: (data) => api.post('/students', data),
  update: (id, data) => api.put(`/students/${id}`, data),
  delete: (id) => api.delete(`/students/${id}`),
  getClasses: () => api.get('/students/classes'),
  bulkImport: (data) => api.post('/students/bulk-import', data),
};

// Staff API
export const staffAPI = {
  getAll: (params) => api.get('/staff', { params }),
  getById: (id) => api.get(`/staff/${id}`),
  create: (data) => api.post('/staff', data),
  update: (id, data) => api.put(`/staff/${id}`, data),
  delete: (id) => api.delete(`/staff/${id}`),
  getPositions: () => api.get('/staff/positions'),
  getDepartments: () => api.get('/staff/departments'),
  getTeachers: () => api.get('/staff/teachers'),
};

// Attendance API
export const attendanceAPI = {
  getAll: (params) => api.get('/attendance', { params }),
  checkIn: (data) => api.post('/attendance/check-in', data),
  checkOut: (data) => api.post('/attendance/check-out', data),
  bulkMark: (data) => api.post('/attendance/bulk-mark', data),
  update: (id, data) => api.put(`/attendance/${id}`, data),
  getReport: (params) => api.get('/attendance/report', { params }),
};

// Grades API
export const gradesAPI = {
  getAll: (params) => api.get('/grades', { params }),
  getById: (id) => api.get(`/grades/${id}`),
  create: (data) => api.post('/grades', data),
  update: (id, data) => api.put(`/grades/${id}`, data),
  delete: (id) => api.delete(`/grades/${id}`),
  getSubjects: () => api.get('/grades/subjects'),
  createSubject: (data) => api.post('/grades/subjects', data),
  bulkCreate: (data) => api.post('/grades/bulk-create', data),
  getStudentReport: (studentId, params) => api.get(`/grades/student/${studentId}/report`, { params }),
  getClassReport: (classId, params) => api.get(`/grades/class/${classId}/report`, { params }),
};

// Fees API
export const feesAPI = {
  getAll: (params) => api.get('/fees', { params }),
  getById: (id) => api.get(`/fees/${id}`),
  create: (data) => api.post('/fees', data),
  update: (id, data) => api.put(`/fees/${id}`, data),
  delete: (id) => api.delete(`/fees/${id}`),
  recordPayment: (id, data) => api.post(`/fees/${id}/payment`, data),
  bulkCreate: (data) => api.post('/fees/bulk-create', data),
  getStudentSummary: (studentId, params) => api.get(`/fees/student/${studentId}/summary`, { params }),
  getReport: (params) => api.get('/fees/report', { params }),
  getOverdue: (params) => api.get('/fees/overdue', { params }),
};

export default api;