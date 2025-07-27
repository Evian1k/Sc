import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const Settings = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">School Settings</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage school configuration and preferences
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🏫 School Information</h3>
          <p className="text-sm text-gray-600 mb-4">
            Update school details, contact information, and branding
          </p>
          <button className="btn btn-primary w-full" disabled>
            Configure
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">👥 User Management</h3>
          <p className="text-sm text-gray-600 mb-4">
            Manage user accounts, roles, and permissions
          </p>
          <button className="btn btn-secondary w-full" disabled>
            Manage Users
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📱 Notifications</h3>
          <p className="text-sm text-gray-600 mb-4">
            Configure SMS, email, and push notification settings
          </p>
          <button className="btn btn-secondary w-full" disabled>
            Configure
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Academic Settings</h3>
          <p className="text-sm text-gray-600 mb-4">
            Set up academic year, terms, grading scale
          </p>
          <button className="btn btn-secondary w-full" disabled>
            Configure
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">💰 Fee Structure</h3>
          <p className="text-sm text-gray-600 mb-4">
            Manage fee types, amounts, and payment settings
          </p>
          <button className="btn btn-secondary w-full" disabled>
            Configure
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🔒 Security</h3>
          <p className="text-sm text-gray-600 mb-4">
            Password policies, backup settings, and security options
          </p>
          <button className="btn btn-secondary w-full" disabled>
            Configure
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🎨 Appearance</h3>
          <p className="text-sm text-gray-600 mb-4">
            Customize colors, logo, and system appearance
          </p>
          <button className="btn btn-secondary w-full" disabled>
            Customize
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🔗 Integrations</h3>
          <p className="text-sm text-gray-600 mb-4">
            Connect with external services and APIs
          </p>
          <button className="btn btn-secondary w-full" disabled>
            Manage
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📥 Backup & Export</h3>
          <p className="text-sm text-gray-600 mb-4">
            Data backup, export, and import settings
          </p>
          <button className="btn btn-secondary w-full" disabled>
            Configure
          </button>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Settings</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">SMS Notifications</h4>
              <p className="text-sm text-gray-600">Send SMS alerts to parents</p>
            </div>
            <input
              type="checkbox"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              disabled
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">Email Notifications</h4>
              <p className="text-sm text-gray-600">Send email notifications</p>
            </div>
            <input
              type="checkbox"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              disabled
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">QR Attendance</h4>
              <p className="text-sm text-gray-600">Enable QR code attendance</p>
            </div>
            <input
              type="checkbox"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              disabled
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;