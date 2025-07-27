import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Classes = () => {
  const { user } = useAuth();
  const [classes, setClasses] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('classes'); // classes, subjects, timetable
  const [showClassModal, setShowClassModal] = useState(false);
  const [showSubjectModal, setShowSubjectModal] = useState(false);
  const [selectedClass, setSelectedClass] = useState(null);
  const [selectedSubject, setSelectedSubject] = useState(null);
  
  const [classForm, setClassForm] = useState({
    name: '',
    description: '',
    academic_year: new Date().getFullYear(),
    term: '1',
    class_teacher_id: '',
    capacity: '',
    room_number: ''
  });

  const [subjectForm, setSubjectForm] = useState({
    name: '',
    code: '',
    description: '',
    teacher_id: '',
    class_id: '',
    credit_hours: '',
    is_mandatory: true
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [classesRes, subjectsRes, teachersRes] = await Promise.all([
        api.get('/classes'),
        api.get('/classes/subjects'),
        api.get('/staff?position=Teacher')
      ]);
      
      setClasses(classesRes.data.classes || []);
      setSubjects(subjectsRes.data.subjects || []);
      setTeachers(teachersRes.data.staff || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateClass = async (e) => {
    e.preventDefault();
    try {
      if (selectedClass) {
        await api.put(`/classes/${selectedClass.id}`, classForm);
      } else {
        await api.post('/classes', classForm);
      }
      setShowClassModal(false);
      setSelectedClass(null);
      resetClassForm();
      fetchData();
      alert('Class saved successfully!');
    } catch (error) {
      console.error('Error saving class:', error);
      alert('Error saving class. Please try again.');
    }
  };

  const handleCreateSubject = async (e) => {
    e.preventDefault();
    try {
      if (selectedSubject) {
        await api.put(`/classes/subjects/${selectedSubject.id}`, subjectForm);
      } else {
        await api.post('/classes/subjects', subjectForm);
      }
      setShowSubjectModal(false);
      setSelectedSubject(null);
      resetSubjectForm();
      fetchData();
      alert('Subject saved successfully!');
    } catch (error) {
      console.error('Error saving subject:', error);
      alert('Error saving subject. Please try again.');
    }
  };

  const resetClassForm = () => {
    setClassForm({
      name: '',
      description: '',
      academic_year: new Date().getFullYear(),
      term: '1',
      class_teacher_id: '',
      capacity: '',
      room_number: ''
    });
  };

  const resetSubjectForm = () => {
    setSubjectForm({
      name: '',
      code: '',
      description: '',
      teacher_id: '',
      class_id: '',
      credit_hours: '',
      is_mandatory: true
    });
  };

  const handleEditClass = (classItem) => {
    setSelectedClass(classItem);
    setClassForm({ ...classItem });
    setShowClassModal(true);
  };

  const handleEditSubject = (subject) => {
    setSelectedSubject(subject);
    setSubjectForm({ ...subject });
    setShowSubjectModal(true);
  };

  const handleDeleteClass = async (classId) => {
    if (window.confirm('Are you sure you want to delete this class? This action cannot be undone.')) {
      try {
        await api.delete(`/classes/${classId}`);
        fetchData();
        alert('Class deleted successfully!');
      } catch (error) {
        console.error('Error deleting class:', error);
        alert('Error deleting class. Please try again.');
      }
    }
  };

  const handleDeleteSubject = async (subjectId) => {
    if (window.confirm('Are you sure you want to delete this subject?')) {
      try {
        await api.delete(`/classes/subjects/${subjectId}`);
        fetchData();
        alert('Subject deleted successfully!');
      } catch (error) {
        console.error('Error deleting subject:', error);
        alert('Error deleting subject. Please try again.');
      }
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
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Class Management</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage classes, subjects, and academic structure
          </p>
        </div>
        {user?.role === 'admin' && (
          <div className="flex space-x-2">
            <button
              onClick={() => setShowClassModal(true)}
              className="btn btn-primary"
            >
              Add Class
            </button>
            <button
              onClick={() => setShowSubjectModal(true)}
              className="btn btn-secondary"
            >
              Add Subject
            </button>
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'classes', name: 'Classes', icon: '🏫' },
            { id: 'subjects', name: 'Subjects', icon: '📚' },
            { id: 'timetable', name: 'Timetable', icon: '⏰' }
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

      {/* Classes Tab */}
      {activeTab === 'classes' && (
        <div className="space-y-6">
          {/* Class Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Total Classes</h3>
              <p className="text-3xl font-bold text-blue-600">{classes.length}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Active Classes</h3>
              <p className="text-3xl font-bold text-green-600">
                {classes.filter(c => c.is_active).length}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Total Subjects</h3>
              <p className="text-3xl font-bold text-purple-600">{subjects.length}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Average Capacity</h3>
              <p className="text-3xl font-bold text-orange-600">
                {classes.length > 0 ? Math.round(classes.reduce((sum, c) => sum + (c.capacity || 0), 0) / classes.length) : 0}
              </p>
            </div>
          </div>

          {/* Classes Table */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Classes</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Class Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Class Teacher
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Room
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Capacity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Students
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    {user?.role === 'admin' && (
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    )}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {classes.map((classItem) => (
                    <tr key={classItem.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{classItem.name}</div>
                        <div className="text-sm text-gray-500">{classItem.description}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {classItem.class_teacher?.first_name} {classItem.class_teacher?.last_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {classItem.room_number || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {classItem.capacity || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {classItem.student_count || 0}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          classItem.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {classItem.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      {user?.role === 'admin' && (
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleEditClass(classItem)}
                              className="text-indigo-600 hover:text-indigo-900"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => handleDeleteClass(classItem.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Subjects Tab */}
      {activeTab === 'subjects' && (
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Subjects</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Subject
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Teacher
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Class
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Credit Hours
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    {user?.role === 'admin' && (
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    )}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {subjects.map((subject) => (
                    <tr key={subject.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{subject.name}</div>
                        <div className="text-sm text-gray-500">{subject.description}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {subject.code}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {subject.teacher?.first_name} {subject.teacher?.last_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {subject.class?.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {subject.credit_hours || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          subject.is_mandatory 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {subject.is_mandatory ? 'Mandatory' : 'Optional'}
                        </span>
                      </td>
                      {user?.role === 'admin' && (
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleEditSubject(subject)}
                              className="text-indigo-600 hover:text-indigo-900"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => handleDeleteSubject(subject.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Timetable Tab */}
      {activeTab === 'timetable' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Class Timetable</h3>
            <p className="text-gray-600">
              Timetable management functionality will be available soon. This will include:
            </p>
            <ul className="mt-4 space-y-2 text-gray-600">
              <li>• Create and manage class schedules</li>
              <li>• Assign subjects to time slots</li>
              <li>• Teacher availability management</li>
              <li>• Room scheduling</li>
              <li>• Conflict detection and resolution</li>
            </ul>
          </div>
        </div>
      )}

      {/* Add/Edit Class Modal */}
      {showClassModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {selectedClass ? 'Edit Class' : 'Add New Class'}
              </h3>
              <form onSubmit={handleCreateClass} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Class Name</label>
                    <input
                      type="text"
                      value={classForm.name}
                      onChange={(e) => setClassForm({ ...classForm, name: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Room Number</label>
                    <input
                      type="text"
                      value={classForm.room_number}
                      onChange={(e) => setClassForm({ ...classForm, room_number: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Class Teacher</label>
                    <select
                      value={classForm.class_teacher_id}
                      onChange={(e) => setClassForm({ ...classForm, class_teacher_id: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="">Select Teacher</option>
                      {teachers.map(teacher => (
                        <option key={teacher.id} value={teacher.id}>
                          {teacher.first_name} {teacher.last_name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Capacity</label>
                    <input
                      type="number"
                      value={classForm.capacity}
                      onChange={(e) => setClassForm({ ...classForm, capacity: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      min="1"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Academic Year</label>
                    <input
                      type="number"
                      value={classForm.academic_year}
                      onChange={(e) => setClassForm({ ...classForm, academic_year: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Term</label>
                    <select
                      value={classForm.term}
                      onChange={(e) => setClassForm({ ...classForm, term: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    >
                      <option value="1">Term 1</option>
                      <option value="2">Term 2</option>
                      <option value="3">Term 3</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    value={classForm.description}
                    onChange={(e) => setClassForm({ ...classForm, description: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows="3"
                  />
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowClassModal(false);
                      setSelectedClass(null);
                      resetClassForm();
                    }}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    {selectedClass ? 'Update' : 'Create'} Class
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Add/Edit Subject Modal */}
      {showSubjectModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {selectedSubject ? 'Edit Subject' : 'Add New Subject'}
              </h3>
              <form onSubmit={handleCreateSubject} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Subject Name</label>
                    <input
                      type="text"
                      value={subjectForm.name}
                      onChange={(e) => setSubjectForm({ ...subjectForm, name: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Subject Code</label>
                    <input
                      type="text"
                      value={subjectForm.code}
                      onChange={(e) => setSubjectForm({ ...subjectForm, code: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Teacher</label>
                    <select
                      value={subjectForm.teacher_id}
                      onChange={(e) => setSubjectForm({ ...subjectForm, teacher_id: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="">Select Teacher</option>
                      {teachers.map(teacher => (
                        <option key={teacher.id} value={teacher.id}>
                          {teacher.first_name} {teacher.last_name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Class</label>
                    <select
                      value={subjectForm.class_id}
                      onChange={(e) => setSubjectForm({ ...subjectForm, class_id: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="">Select Class</option>
                      {classes.map(classItem => (
                        <option key={classItem.id} value={classItem.id}>
                          {classItem.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Credit Hours</label>
                    <input
                      type="number"
                      value={subjectForm.credit_hours}
                      onChange={(e) => setSubjectForm({ ...subjectForm, credit_hours: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      min="1"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Subject Type</label>
                    <select
                      value={subjectForm.is_mandatory}
                      onChange={(e) => setSubjectForm({ ...subjectForm, is_mandatory: e.target.value === 'true' })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="true">Mandatory</option>
                      <option value="false">Optional</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    value={subjectForm.description}
                    onChange={(e) => setSubjectForm({ ...subjectForm, description: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows="3"
                  />
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowSubjectModal(false);
                      setSelectedSubject(null);
                      resetSubjectForm();
                    }}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    {selectedSubject ? 'Update' : 'Create'} Subject
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Classes;