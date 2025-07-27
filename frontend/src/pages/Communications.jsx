import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const Communications = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Communications</h1>
          <p className="mt-1 text-sm text-gray-600">
            SMS, Email, and messaging system
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Messages Sent</h3>
          <p className="text-3xl font-bold text-blue-600">0</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">SMS Sent</h3>
          <p className="text-3xl font-bold text-green-600">0</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Emails Sent</h3>
          <p className="text-3xl font-bold text-purple-600">0</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Communication Tools</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">📧 Send Email</h4>
            <p className="text-sm text-gray-600 mb-4">
              Send emails to students, parents, or staff
            </p>
            <button className="btn btn-primary w-full" disabled>
              Coming Soon
            </button>
          </div>
          
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">📱 Send SMS</h4>
            <p className="text-sm text-gray-600 mb-4">
              Send SMS notifications and alerts
            </p>
            <button className="btn btn-secondary w-full" disabled>
              Coming Soon
            </button>
          </div>
          
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">📢 Broadcast</h4>
            <p className="text-sm text-gray-600 mb-4">
              Send messages to multiple recipients
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

export default Communications;