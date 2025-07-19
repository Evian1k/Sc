import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  AcademicCapIcon,
  UserGroupIcon,
  ClipboardDocumentListIcon,
  BanknotesIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';
import { studentsAPI, staffAPI, attendanceAPI, feesAPI, gradesAPI } from '../services/api';

function StatCard({ title, value, icon: Icon, color = 'blue' }) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    purple: 'bg-purple-500',
  };

  return (
    <div className="card">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <div className={`w-8 h-8 ${colorClasses[color]} rounded-md flex items-center justify-center`}>
            <Icon className="w-5 h-5 text-white" />
          </div>
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="text-lg font-medium text-gray-900">{value}</dd>
          </dl>
        </div>
      </div>
    </div>
  );
}

function RecentActivity({ activities }) {
  return (
    <div className="card">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
      <div className="space-y-3">
        {activities.length > 0 ? (
          activities.map((activity, index) => (
            <div key={index} className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900">{activity.message}</p>
                <p className="text-xs text-gray-500">{activity.time}</p>
              </div>
            </div>
          ))
        ) : (
          <p className="text-sm text-gray-500">No recent activity</p>
        )}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { user, profile } = useAuth();
  const [stats, setStats] = useState({
    totalStudents: 0,
    totalStaff: 0,
    presentToday: 0,
    pendingFees: 0,
    averageGrade: 0,
  });
  const [loading, setLoading] = useState(true);
  const [recentActivity] = useState([
    { message: 'New student Alice Johnson enrolled', time: '2 hours ago' },
    { message: 'Attendance marked for Grade 5A', time: '4 hours ago' },
    { message: 'Fee payment received from Bob Smith', time: '6 hours ago' },
    { message: 'Math test grades uploaded', time: '1 day ago' },
    { message: 'New teacher John Doe added to staff', time: '2 days ago' },
  ]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch students data
      const studentsResponse = await studentsAPI.getAll({ per_page: 1 });
      const totalStudents = studentsResponse.data.total || 0;

      // Fetch staff data if admin
      let totalStaff = 0;
      if (user?.role === 'admin') {
        const staffResponse = await staffAPI.getAll({ per_page: 1 });
        totalStaff = staffResponse.data.total || 0;
      }

      // Fetch attendance data
      const today = new Date().toISOString().split('T')[0];
      const attendanceResponse = await attendanceAPI.getAll({ 
        date: today, 
        status: 'present',
        per_page: 1 
      });
      const presentToday = attendanceResponse.data.total || 0;

      // Fetch pending fees
      const feesResponse = await feesAPI.getAll({ 
        status: 'pending',
        per_page: 1 
      });
      const pendingFees = feesResponse.data.total || 0;

      setStats({
        totalStudents,
        totalStaff,
        presentToday,
        pendingFees,
        averageGrade: 85.5, // Mock data for average grade
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatsForRole = () => {
    const allStats = [
      {
        title: 'Total Students',
        value: loading ? '...' : stats.totalStudents,
        icon: AcademicCapIcon,
        color: 'blue',
        roles: ['admin', 'teacher'],
      },
      {
        title: 'Total Staff',
        value: loading ? '...' : stats.totalStaff,
        icon: UserGroupIcon,
        color: 'green',
        roles: ['admin'],
      },
      {
        title: 'Present Today',
        value: loading ? '...' : stats.presentToday,
        icon: ClipboardDocumentListIcon,
        color: 'yellow',
        roles: ['admin', 'teacher'],
      },
      {
        title: 'Pending Fees',
        value: loading ? '...' : stats.pendingFees,
        icon: BanknotesIcon,
        color: 'red',
        roles: ['admin'],
      },
      {
        title: 'Average Grade',
        value: loading ? '...' : `${stats.averageGrade}%`,
        icon: ChartBarIcon,
        color: 'purple',
        roles: ['admin', 'teacher'],
      },
    ];

    return allStats.filter(stat => stat.roles.includes(user?.role));
  };

  const getWelcomeMessage = () => {
    const hour = new Date().getHours();
    const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
    const name = profile?.first_name || user?.username || 'User';
    
    return `${greeting}, ${name}!`;
  };

  const getRoleSpecificContent = () => {
    switch (user?.role) {
      case 'admin':
        return (
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Admin Quick Actions</h3>
            <div className="grid grid-cols-2 gap-4">
              <button className="btn-primary text-sm">Add Student</button>
              <button className="btn-primary text-sm">Add Staff</button>
              <button className="btn-secondary text-sm">View Reports</button>
              <button className="btn-secondary text-sm">Manage Fees</button>
            </div>
          </div>
        );
      case 'teacher':
        return (
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Teacher Quick Actions</h3>
            <div className="grid grid-cols-2 gap-4">
              <button className="btn-primary text-sm">Mark Attendance</button>
              <button className="btn-primary text-sm">Add Grades</button>
              <button className="btn-secondary text-sm">View Students</button>
              <button className="btn-secondary text-sm">Class Reports</button>
            </div>
          </div>
        );
      case 'student':
        return (
          <div className="card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Student Information</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Student ID:</span>
                <span className="text-sm font-medium">{profile?.student_id || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Class:</span>
                <span className="text-sm font-medium">{profile?.class_name || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Admission Date:</span>
                <span className="text-sm font-medium">
                  {profile?.admission_date ? new Date(profile.admission_date).toLocaleDateString() : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="card">
        <h1 className="text-2xl font-bold text-gray-900">{getWelcomeMessage()}</h1>
        <p className="mt-1 text-sm text-gray-600">
          Welcome to EduManage Pro - Your comprehensive school management system
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        {getStatsForRole().map((stat, index) => (
          <StatCard
            key={index}
            title={stat.title}
            value={stat.value}
            icon={stat.icon}
            color={stat.color}
          />
        ))}
      </div>

      {/* Role-specific content and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {getRoleSpecificContent()}
        <RecentActivity activities={recentActivity} />
      </div>

      {/* Additional Information */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">System Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Academic Year:</span>
            <span className="ml-2 font-medium">2023-2024</span>
          </div>
          <div>
            <span className="text-gray-600">Current Semester:</span>
            <span className="ml-2 font-medium">Fall 2023</span>
          </div>
          <div>
            <span className="text-gray-600">System Status:</span>
            <span className="ml-2 font-medium text-green-600">Online</span>
          </div>
        </div>
      </div>
    </div>
  );
}