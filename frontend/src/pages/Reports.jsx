import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const Reports = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="mt-1 text-sm text-gray-600">
            Generate reports and view analytics
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Student Reports</h3>
          <p className="text-3xl font-bold text-blue-600">0</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Financial Reports</h3>
          <p className="text-3xl font-bold text-green-600">0</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Attendance Reports</h3>
          <p className="text-3xl font-bold text-orange-600">0</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Grade Reports</h3>
          <p className="text-3xl font-bold text-purple-600">0</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Available Reports</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">📊 Academic Performance</h4>
            <p className="text-sm text-gray-600 mb-4">
              Class and subject performance analysis
            </p>
            <button className="btn btn-primary w-full" disabled>
              Coming Soon
            </button>
          </div>
          
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">💰 Financial Summary</h4>
            <p className="text-sm text-gray-600 mb-4">
              Fee collection and financial reports
            </p>
            <button className="btn btn-secondary w-full" disabled>
              Coming Soon
            </button>
          </div>
          
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">📅 Attendance Summary</h4>
            <p className="text-sm text-gray-600 mb-4">
              Student attendance patterns and statistics
            </p>
            <button className="btn btn-secondary w-full" disabled>
              Coming Soon
            </button>
          </div>
          
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">🎓 Student Report Cards</h4>
            <p className="text-sm text-gray-600 mb-4">
              Individual student academic reports
            </p>
            <button className="btn btn-secondary w-full" disabled>
              Coming Soon
            </button>
          </div>
          
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">📈 Exam Analytics</h4>
            <p className="text-sm text-gray-600 mb-4">
              Examination performance and trends
            </p>
            <button className="btn btn-secondary w-full" disabled>
              Coming Soon
            </button>
          </div>
          
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">👥 Staff Reports</h4>
            <p className="text-sm text-gray-600 mb-4">
              Staff performance and management reports
            </p>
            <button className="btn btn-secondary w-full" disabled>
              Coming Soon
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;