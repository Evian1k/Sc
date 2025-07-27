import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Events = () => {
  const { user } = useAuth();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const response = await api.get('/events');
      setEvents(response.data.events || []);
    } catch (error) {
      console.error('Error fetching events:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Events & Calendar</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage school events and calendar
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Total Events</h3>
          <p className="text-3xl font-bold text-blue-600">{events.length}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Upcoming</h3>
          <p className="text-3xl font-bold text-green-600">
            {events.filter(e => new Date(e.start_date) > new Date()).length}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">This Month</h3>
          <p className="text-3xl font-bold text-purple-600">
            {events.filter(e => {
              const eventDate = new Date(e.start_date);
              const now = new Date();
              return eventDate.getMonth() === now.getMonth() && eventDate.getFullYear() === now.getFullYear();
            }).length}
          </p>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Events</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {events.length > 0 ? events.map((event) => (
            <div key={event.id} className="p-6">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <span className="text-blue-600 text-sm">📅</span>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900">
                    {event.title}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {event.description}
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    {new Date(event.start_date).toLocaleDateString()} - {event.venue}
                  </div>
                </div>
              </div>
            </div>
          )) : (
            <div className="p-6 text-center">
              <p className="text-gray-500">No events available.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Events;