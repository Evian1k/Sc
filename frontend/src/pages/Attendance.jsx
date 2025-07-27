import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Attendance = () => {
  const { user } = useAuth();
  const [attendanceData, setAttendanceData] = useState([]);
  const [classes, setClasses] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedClass, setSelectedClass] = useState('');
  const [attendanceMarks, setAttendanceMarks] = useState({});
  const [showQRModal, setShowQRModal] = useState(false);
  const [qrCode, setQrCode] = useState('');
  const [analytics, setAnalytics] = useState(null);
  const [activeTab, setActiveTab] = useState('mark'); // mark, view, qr, analytics

  useEffect(() => {
    fetchClasses();
    fetchAnalytics();
  }, []);

  useEffect(() => {
    if (selectedClass && selectedDate) {
      fetchAttendanceForClass();
    }
  }, [selectedClass, selectedDate]);

  const fetchClasses = async () => {
    try {
      const response = await api.get('/classes');
      setClasses(response.data.classes || []);
    } catch (error) {
      console.error('Error fetching classes:', error);
    }
  };

  const fetchAttendanceForClass = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/attendance?class_id=${selectedClass}&date=${selectedDate}`);
      setAttendanceData(response.data.attendance || []);
      
      // Fetch students for the selected class
      const studentsResponse = await api.get(`/students?class_id=${selectedClass}`);
      setStudents(studentsResponse.data.students || []);
      
      // Initialize attendance marks
      const marks = {};
      studentsResponse.data.students?.forEach(student => {
        const existingAttendance = response.data.attendance?.find(a => a.student_id === student.id);
        marks[student.id] = existingAttendance ? existingAttendance.status : 'present';
      });
      setAttendanceMarks(marks);
    } catch (error) {
      console.error('Error fetching attendance:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/attendance/analytics');
      setAnalytics(response.data.analytics);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const markAttendance = async () => {
    try {
      const attendanceEntries = students.map(student => ({
        student_id: student.id,
        class_id: parseInt(selectedClass),
        date: selectedDate,
        status: attendanceMarks[student.id] || 'present',
        marked_by_id: user.id
      }));

      await api.post('/attendance/bulk', { attendance_entries: attendanceEntries });
      alert('Attendance marked successfully!');
      fetchAttendanceForClass();
    } catch (error) {
      console.error('Error marking attendance:', error);
      alert('Error marking attendance. Please try again.');
    }
  };

  const generateQRCode = async () => {
    try {
      const response = await api.post(`/qr/class/${selectedClass}/generate`, {
        valid_minutes: 60
      });
      setQrCode(response.data.qr_image_base64);
      setShowQRModal(true);
    } catch (error) {
      console.error('Error generating QR code:', error);
      alert('Error generating QR code. Please try again.');
    }
  };

  const handleAttendanceChange = (studentId, status) => {
    setAttendanceMarks({
      ...attendanceMarks,
      [studentId]: status
    });
  };

  const getAttendanceStats = () => {
    if (!attendanceData.length) return { present: 0, absent: 0, late: 0, total: 0 };
    
    const present = attendanceData.filter(a => a.status === 'present').length;
    const absent = attendanceData.filter(a => a.status === 'absent').length;
    const late = attendanceData.filter(a => a.status === 'late').length;
    
    return { present, absent, late, total: attendanceData.length };
  };

  const stats = getAttendanceStats();

  if (loading && activeTab === 'mark') {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Attendance Management</h1>
          <p className="mt-1 text-sm text-gray-600">
            Track and manage student attendance with multiple methods
          </p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'mark', name: 'Mark Attendance', icon: '✓' },
            { id: 'view', name: 'View Records', icon: '📋' },
            { id: 'qr', name: 'QR Attendance', icon: '📱' },
            { id: 'analytics', name: 'Analytics', icon: '📊' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Mark Attendance Tab */}
      {activeTab === 'mark' && (
        <div className="space-y-6">
          {/* Controls */}
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Select Date</label>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Select Class</label>
                <select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">Choose a class</option>
                  {classes.map(cls => (
                    <option key={cls.id} value={cls.id}>
                      {cls.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={markAttendance}
                  disabled={!selectedClass || !students.length}
                  className="btn btn-primary w-full"
                >
                  Save Attendance
                </button>
              </div>
            </div>
          </div>

          {/* Attendance Stats */}
          {selectedClass && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900">Total Students</h3>
                <p className="text-3xl font-bold text-blue-600">{students.length}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900">Present</h3>
                <p className="text-3xl font-bold text-green-600">
                  {Object.values(attendanceMarks).filter(status => status === 'present').length}
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900">Absent</h3>
                <p className="text-3xl font-bold text-red-600">
                  {Object.values(attendanceMarks).filter(status => status === 'absent').length}
                </p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900">Late</h3>
                <p className="text-3xl font-bold text-yellow-600">
                  {Object.values(attendanceMarks).filter(status => status === 'late').length}
                </p>
              </div>
            </div>
          )}

          {/* Student List */}
          {selectedClass && students.length > 0 && (
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">
                  Students - {classes.find(c => c.id == selectedClass)?.name}
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Student
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Student ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Attendance Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {students.map((student) => (
                      <tr key={student.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                              <span className="text-sm font-medium text-gray-700">
                                {student.first_name?.charAt(0)}{student.last_name?.charAt(0)}
                              </span>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">
                                {student.first_name} {student.last_name}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {student.student_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex space-x-2">
                            {['present', 'absent', 'late'].map(status => (
                              <label key={status} className="flex items-center">
                                <input
                                  type="radio"
                                  name={`attendance-${student.id}`}
                                  value={status}
                                  checked={attendanceMarks[student.id] === status}
                                  onChange={() => handleAttendanceChange(student.id, status)}
                                  className="mr-1"
                                />
                                <span className={`text-sm capitalize ${
                                  status === 'present' ? 'text-green-600' :
                                  status === 'absent' ? 'text-red-600' :
                                  'text-yellow-600'
                                }`}>
                                  {status}
                                </span>
                              </label>
                            ))}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* QR Attendance Tab */}
      {activeTab === 'qr' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">QR Code Attendance</h3>
            <p className="text-gray-600 mb-4">
              Generate QR codes for students to scan and mark their attendance automatically.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Select Class</label>
                <select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">Choose a class</option>
                  {classes.map(cls => (
                    <option key={cls.id} value={cls.id}>
                      {cls.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={generateQRCode}
                  disabled={!selectedClass}
                  className="btn btn-primary w-full"
                >
                  Generate QR Code
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && analytics && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Overall Attendance Rate</h3>
              <p className="text-3xl font-bold text-blue-600">
                {analytics.overall_attendance_rate?.toFixed(1)}%
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Today's Attendance</h3>
              <p className="text-3xl font-bold text-green-600">
                {analytics.today_attendance_rate?.toFixed(1)}%
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">This Week Average</h3>
              <p className="text-3xl font-bold text-purple-600">
                {analytics.week_average?.toFixed(1)}%
              </p>
            </div>
          </div>

          {/* Class-wise Attendance */}
          {analytics.class_wise && (
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Class-wise Attendance</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Class
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Total Students
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Attendance Rate
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.entries(analytics.class_wise).map(([className, data]) => (
                      <tr key={className} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {className}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {data.total_students}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {data.attendance_rate?.toFixed(1)}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            data.attendance_rate >= 90 
                              ? 'bg-green-100 text-green-800'
                              : data.attendance_rate >= 75
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {data.attendance_rate >= 90 ? 'Excellent' : 
                             data.attendance_rate >= 75 ? 'Good' : 'Needs Attention'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* QR Code Modal */}
      {showQRModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                QR Code for Attendance
              </h3>
              {qrCode && (
                <div className="mb-4">
                  <img 
                    src={`data:image/png;base64,${qrCode}`} 
                    alt="QR Code" 
                    className="mx-auto"
                  />
                </div>
              )}
              <p className="text-sm text-gray-600 mb-4">
                Students can scan this QR code to mark their attendance.
                QR code is valid for 60 minutes.
              </p>
              <button
                onClick={() => {
                  setShowQRModal(false);
                  setQrCode('');
                }}
                className="btn btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Attendance;