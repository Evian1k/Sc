import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';

// Import all pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Students from './pages/Students';
import Staff from './pages/Staff';
import Attendance from './pages/Attendance';
import Fees from './pages/Fees';
import Exams from './pages/Exams';

import Classes from './pages/Classes';
import Grades from './pages/Grades';
import Parents from './pages/Parents';

function Library() {
  return (
    <div className="space-y-6">
      <div className="card">
        <h1 className="text-2xl font-bold text-gray-900">Library Management</h1>
        <p className="mt-2 text-gray-600">Manage library books, borrowing, and inventory</p>
      </div>
    </div>
  );
}

function Events() {
  return (
    <div className="space-y-6">
      <div className="card">
        <h1 className="text-2xl font-bold text-gray-900">Events & Calendar</h1>
        <p className="mt-2 text-gray-600">Manage school events and calendar</p>
      </div>
    </div>
  );
}

function Communications() {
  return (
    <div className="space-y-6">
      <div className="card">
        <h1 className="text-2xl font-bold text-gray-900">Communications</h1>
        <p className="mt-2 text-gray-600">SMS, Email, and messaging system</p>
      </div>
    </div>
  );
}

function Reports() {
  return (
    <div className="space-y-6">
      <div className="card">
        <h1 className="text-2xl font-bold text-gray-900">Reports & Analytics</h1>
        <p className="mt-2 text-gray-600">Generate reports and view analytics</p>
      </div>
    </div>
  );
}

function Settings() {
  return (
    <div className="space-y-6">
      <div className="card">
        <h1 className="text-2xl font-bold text-gray-900">School Settings</h1>
        <p className="mt-2 text-gray-600">Manage school configuration and preferences</p>
      </div>
    </div>
  );
}

// Protected Route component
function ProtectedRoute({ children, allowedRoles = [] }) {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/" replace />;
  }

  return children;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={
        <ProtectedRoute>
          <Layout>
            <Dashboard />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Student Management */}
      <Route path="/students" element={
        <ProtectedRoute allowedRoles={['admin', 'teacher']}>
          <Layout>
            <Students />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Staff Management */}
      <Route path="/staff" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <Layout>
            <Staff />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Attendance */}
      <Route path="/attendance" element={
        <ProtectedRoute allowedRoles={['admin', 'teacher']}>
          <Layout>
            <Attendance />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Classes */}
      <Route path="/classes" element={
        <ProtectedRoute allowedRoles={['admin', 'teacher']}>
          <Layout>
            <Classes />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Grades */}
      <Route path="/grades" element={
        <ProtectedRoute allowedRoles={['admin', 'teacher', 'student', 'parent']}>
          <Layout>
            <Grades />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Exams */}
      <Route path="/exams" element={
        <ProtectedRoute allowedRoles={['admin', 'teacher', 'student']}>
          <Layout>
            <Exams />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Fees */}
      <Route path="/fees" element={
        <ProtectedRoute allowedRoles={['admin', 'accountant', 'student', 'parent']}>
          <Layout>
            <Fees />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Parent Portal */}
      <Route path="/parents" element={
        <ProtectedRoute allowedRoles={['admin', 'parent']}>
          <Layout>
            <Parents />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Library */}
      <Route path="/library" element={
        <ProtectedRoute allowedRoles={['admin', 'teacher', 'student']}>
          <Layout>
            <Library />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Events */}
      <Route path="/events" element={
        <ProtectedRoute>
          <Layout>
            <Events />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Communications */}
      <Route path="/communications" element={
        <ProtectedRoute allowedRoles={['admin', 'teacher']}>
          <Layout>
            <Communications />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Reports */}
      <Route path="/reports" element={
        <ProtectedRoute allowedRoles={['admin', 'teacher', 'accountant']}>
          <Layout>
            <Reports />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Settings */}
      <Route path="/settings" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <Layout>
            <Settings />
          </Layout>
        </ProtectedRoute>
      } />
      
      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppRoutes />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;