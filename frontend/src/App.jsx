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
import Library from './pages/Library';
import Events from './pages/Events';
import Communications from './pages/Communications';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

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