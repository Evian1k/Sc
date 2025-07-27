import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Parents = () => {
  const { user } = useAuth();
  const [parentData, setParentData] = useState(null);
  const [children, setChildren] = useState([]);
  const [selectedChild, setSelectedChild] = useState(null);
  const [childAttendance, setChildAttendance] = useState([]);
  const [childGrades, setChildGrades] = useState([]);
  const [childFees, setChildFees] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // overview, attendance, grades, fees, notifications

  useEffect(() => {
    if (user?.role === 'parent') {
      fetchParentData();
    }
  }, [user]);

  useEffect(() => {
    if (selectedChild) {
      fetchChildData();
    }
  }, [selectedChild]);

  const fetchParentData = async () => {
    try {
      setLoading(true);
      const [parentRes, notificationsRes] = await Promise.all([
        api.get('/parents'),
        api.get('/notifications/history')
      ]);
      
      if (parentRes.data.parent) {
        setParentData(parentRes.data.parent);
        // Fetch children
        const childrenRes = await api.get(`/parents/${parentRes.data.parent.id}/children`);
        setChildren(childrenRes.data.children || []);
        
        if (childrenRes.data.children?.length > 0) {
          setSelectedChild(childrenRes.data.children[0]);
        }
      }
      
      setNotifications(notificationsRes.data.notifications || []);
    } catch (error) {
      console.error('Error fetching parent data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchChildData = async () => {
    if (!selectedChild || !parentData) return;
    
    try {
      const [attendanceRes, gradesRes, feesRes] = await Promise.all([
        api.get(`/parents/${parentData.id}/child/${selectedChild.id}/attendance`),
        api.get(`/grades?student_id=${selectedChild.id}&academic_year=${new Date().getFullYear()}`),
        api.get(`/fees?student_id=${selectedChild.id}`)
      ]);
      
      setChildAttendance(attendanceRes.data.attendance || []);
      setChildGrades(gradesRes.data.grades || []);
      setChildFees(feesRes.data.fees || []);
    } catch (error) {
      console.error('Error fetching child data:', error);
    }
  };

  const calculateAttendanceRate = () => {
    if (!childAttendance.length) return 0;
    const presentDays = childAttendance.filter(a => a.status === 'present').length;
    return ((presentDays / childAttendance.length) * 100).toFixed(1);
  };

  const calculateAverageGrade = () => {
    if (!childGrades.length) return 0;
    const totalPercentage = childGrades.reduce((sum, grade) => sum + (grade.percentage || 0), 0);
    return (totalPercentage / childGrades.length).toFixed(1);
  };

  const calculateFeeBalance = () => {
    return childFees.reduce((sum, fee) => sum + (fee.amount - fee.amount_paid), 0);
  };

  const getGradeColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 70) return 'text-blue-600';
    if (percentage >= 60) return 'text-yellow-600';
    if (percentage >= 50) return 'text-orange-600';
    return 'text-red-600';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (user?.role !== 'parent' || !parentData) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Parent portal is only accessible to parent accounts.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Parent Portal</h1>
          <p className="mt-1 text-sm text-gray-600">
            Welcome, {parentData.user?.first_name} {parentData.user?.last_name}
          </p>
        </div>
      </div>

      {/* Child Selector */}
      {children.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Select Child</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {children.map((child) => (
              <button
                key={child.id}
                onClick={() => setSelectedChild(child)}
                className={`p-4 border-2 rounded-lg text-left transition-colors ${
                  selectedChild?.id === child.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className="h-12 w-12 rounded-full bg-gray-200 flex items-center justify-center">
                    <span className="text-lg font-medium text-gray-700">
                      {child.first_name?.charAt(0)}{child.last_name?.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">
                      {child.first_name} {child.last_name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {child.class_enrolled?.name} - {child.student_id}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {selectedChild && (
        <>
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Attendance Rate</h3>
              <p className="text-3xl font-bold text-blue-600">{calculateAttendanceRate()}%</p>
              <p className="text-sm text-gray-500">This term</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Average Grade</h3>
              <p className={`text-3xl font-bold ${getGradeColor(calculateAverageGrade())}`}>
                {calculateAverageGrade()}%
              </p>
              <p className="text-sm text-gray-500">All subjects</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Fee Balance</h3>
              <p className="text-3xl font-bold text-red-600">
                {formatCurrency(calculateFeeBalance())}
              </p>
              <p className="text-sm text-gray-500">Outstanding</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Class Rank</h3>
              <p className="text-3xl font-bold text-purple-600">--</p>
              <p className="text-sm text-gray-500">Coming soon</p>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'overview', name: 'Overview', icon: '👁️' },
                { id: 'attendance', name: 'Attendance', icon: '📅' },
                { id: 'grades', name: 'Grades', icon: '📊' },
                { id: 'fees', name: 'Fees', icon: '💰' },
                { id: 'notifications', name: 'Messages', icon: '📧' }
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

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Child Information */}
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Student Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <div className="space-y-3">
                      <div>
                        <label className="text-sm font-medium text-gray-500">Full Name</label>
                        <p className="text-sm text-gray-900">{selectedChild.first_name} {selectedChild.last_name}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Student ID</label>
                        <p className="text-sm text-gray-900">{selectedChild.student_id}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Class</label>
                        <p className="text-sm text-gray-900">{selectedChild.class_enrolled?.name}</p>
                      </div>
                    </div>
                  </div>
                  <div>
                    <div className="space-y-3">
                      <div>
                        <label className="text-sm font-medium text-gray-500">Date of Birth</label>
                        <p className="text-sm text-gray-900">
                          {selectedChild.date_of_birth ? new Date(selectedChild.date_of_birth).toLocaleDateString() : 'N/A'}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Gender</label>
                        <p className="text-sm text-gray-900">{selectedChild.gender}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-500">Admission Date</label>
                        <p className="text-sm text-gray-900">
                          {selectedChild.admission_date ? new Date(selectedChild.admission_date).toLocaleDateString() : 'N/A'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
                <div className="space-y-4">
                  {/* Recent Attendance */}
                  <div className="border-l-4 border-blue-500 pl-4">
                    <h4 className="font-medium text-gray-900">Latest Attendance</h4>
                    <p className="text-sm text-gray-600">
                      {childAttendance.length > 0 
                        ? `${childAttendance[0].status.charAt(0).toUpperCase() + childAttendance[0].status.slice(1)} on ${new Date(childAttendance[0].date).toLocaleDateString()}`
                        : 'No attendance records available'
                      }
                    </p>
                  </div>

                  {/* Recent Grade */}
                  <div className="border-l-4 border-green-500 pl-4">
                    <h4 className="font-medium text-gray-900">Latest Grade</h4>
                    <p className="text-sm text-gray-600">
                      {childGrades.length > 0 
                        ? `${childGrades[0].subject?.name}: ${childGrades[0].percentage?.toFixed(1)}%`
                        : 'No grade records available'
                      }
                    </p>
                  </div>

                  {/* Recent Fee Payment */}
                  <div className="border-l-4 border-yellow-500 pl-4">
                    <h4 className="font-medium text-gray-900">Fee Status</h4>
                    <p className="text-sm text-gray-600">
                      {calculateFeeBalance() > 0 
                        ? `Outstanding balance: ${formatCurrency(calculateFeeBalance())}`
                        : 'All fees are up to date'
                      }
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Attendance Tab */}
          {activeTab === 'attendance' && (
            <div className="space-y-6">
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Attendance Records</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Check In Time
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Notes
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {childAttendance.map((attendance) => (
                        <tr key={attendance.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {new Date(attendance.date).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              attendance.status === 'present' 
                                ? 'bg-green-100 text-green-800'
                                : attendance.status === 'late'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {attendance.status.charAt(0).toUpperCase() + attendance.status.slice(1)}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {attendance.check_in_time || 'N/A'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {attendance.notes || 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Grades Tab */}
          {activeTab === 'grades' && (
            <div className="space-y-6">
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Grade Records</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Subject
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Assessment
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Score
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Grade
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {childGrades.map((grade) => (
                        <tr key={grade.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {grade.subject?.name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {grade.assessment_type}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {grade.score}/{grade.total_marks} ({grade.percentage?.toFixed(1)}%)
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`text-sm font-semibold ${getGradeColor(grade.percentage)}`}>
                              {grade.percentage >= 90 ? 'A+' :
                               grade.percentage >= 80 ? 'A' :
                               grade.percentage >= 70 ? 'B' :
                               grade.percentage >= 60 ? 'C' :
                               grade.percentage >= 50 ? 'D' : 'F'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {new Date(grade.assessment_date).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Fees Tab */}
          {activeTab === 'fees' && (
            <div className="space-y-6">
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Fee Records</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Fee Type
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Amount
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Paid
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Balance
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Due Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {childFees.map((fee) => {
                        const balance = fee.amount - fee.amount_paid;
                        const isOverdue = new Date(fee.due_date) < new Date() && balance > 0;
                        return (
                          <tr key={fee.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {fee.fee_type}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatCurrency(fee.amount)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatCurrency(fee.amount_paid)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatCurrency(balance)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {new Date(fee.due_date).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                balance === 0 
                                  ? 'bg-green-100 text-green-800'
                                  : isOverdue
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {balance === 0 ? 'Paid' : isOverdue ? 'Overdue' : 'Pending'}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Messages & Notifications</h3>
                </div>
                <div className="divide-y divide-gray-200">
                  {notifications.map((notification) => (
                    <div key={notification.id} className="p-6">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                            <span className="text-blue-600 text-sm">📧</span>
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-gray-900">
                            {notification.subject}
                          </div>
                          <div className="text-sm text-gray-600 mt-1">
                            {notification.content}
                          </div>
                          <div className="text-xs text-gray-500 mt-2">
                            {new Date(notification.created_at).toLocaleDateString()} at {' '}
                            {new Date(notification.created_at).toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {notifications.length === 0 && (
                    <div className="p-6 text-center">
                      <p className="text-gray-500">No notifications available.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {children.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500">No children found in your account. Please contact the school administration.</p>
        </div>
      )}
    </div>
  );
};

export default Parents;