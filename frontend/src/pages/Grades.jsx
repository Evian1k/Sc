import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Grades = () => {
  const { user } = useAuth();
  const [grades, setGrades] = useState([]);
  const [students, setStudents] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // overview, grades, reports
  const [selectedClass, setSelectedClass] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedStudent, setSelectedStudent] = useState('');
  const [academicYear, setAcademicYear] = useState(new Date().getFullYear());
  const [term, setTerm] = useState('1');
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (activeTab === 'grades') {
      fetchGrades();
    } else if (activeTab === 'overview') {
      fetchAnalytics();
    }
  }, [activeTab, selectedClass, selectedSubject, selectedStudent, academicYear, term]);

  const fetchData = async () => {
    try {
      setLoading(true);
             const [studentsRes, subjectsRes, classesRes] = await Promise.all([
         api.get('/students'),
         api.get('/classes/subjects'),
         api.get('/classes')
       ]);
      
      setStudents(studentsRes.data.students || []);
      setSubjects(subjectsRes.data.subjects || []);
      setClasses(classesRes.data.classes || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchGrades = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedClass) params.append('class_id', selectedClass);
      if (selectedSubject) params.append('subject_id', selectedSubject);
      if (selectedStudent) params.append('student_id', selectedStudent);
      params.append('academic_year', academicYear);
      params.append('term', term);

      const response = await api.get(`/grades?${params.toString()}`);
      setGrades(response.data.grades || []);
    } catch (error) {
      console.error('Error fetching grades:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const params = new URLSearchParams();
      params.append('academic_year', academicYear);
      params.append('term', term);
      if (selectedClass) params.append('class_id', selectedClass);

      const response = await api.get(`/grades/analytics?${params.toString()}`);
      setAnalytics(response.data.analytics);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const calculateGrade = (percentage) => {
    if (percentage >= 90) return { grade: 'A+', color: 'text-green-600' };
    if (percentage >= 80) return { grade: 'A', color: 'text-green-600' };
    if (percentage >= 70) return { grade: 'B', color: 'text-blue-600' };
    if (percentage >= 60) return { grade: 'C', color: 'text-yellow-600' };
    if (percentage >= 50) return { grade: 'D', color: 'text-orange-600' };
    return { grade: 'F', color: 'text-red-600' };
  };

  const getPerformanceStatus = (percentage) => {
    if (percentage >= 80) return { status: 'Excellent', color: 'bg-green-100 text-green-800' };
    if (percentage >= 70) return { status: 'Good', color: 'bg-blue-100 text-blue-800' };
    if (percentage >= 60) return { status: 'Satisfactory', color: 'bg-yellow-100 text-yellow-800' };
    if (percentage >= 50) return { status: 'Pass', color: 'bg-orange-100 text-orange-800' };
    return { status: 'Fail', color: 'bg-red-100 text-red-800' };
  };

  const generateReport = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedStudent) params.append('student_id', selectedStudent);
      params.append('academic_year', academicYear);
      params.append('term', term);

      const response = await api.post(`/reports/student/${selectedStudent}/report-card`, {
        academic_year: academicYear,
        term: term
      });

      if (response.data.success) {
        // Handle PDF download or display
        alert('Report card generated successfully!');
      }
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Error generating report. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Filter students based on user role
  const filteredStudents = user?.role === 'student' 
    ? students.filter(s => s.user_id === user.id)
    : user?.role === 'parent'
    ? students.filter(s => s.parent_id === user.parent_id)
    : students;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Grade Management</h1>
          <p className="mt-1 text-sm text-gray-600">
            View and manage academic performance and grades
          </p>
        </div>
        {user?.role === 'student' && selectedStudent && (
          <button
            onClick={generateReport}
            className="btn btn-primary"
          >
            Generate Report Card
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Academic Year</label>
            <select
              value={academicYear}
              onChange={(e) => setAcademicYear(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
            >
              {[2024, 2023, 2022].map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Term</label>
            <select
              value={term}
              onChange={(e) => setTerm(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="1">Term 1</option>
              <option value="2">Term 2</option>
              <option value="3">Term 3</option>
            </select>
          </div>
          {user?.role !== 'student' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700">Class</label>
                <select
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">All Classes</option>
                  {classes.map(cls => (
                    <option key={cls.id} value={cls.id}>{cls.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Subject</label>
                <select
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">All Subjects</option>
                  {subjects.map(subject => (
                    <option key={subject.id} value={subject.id}>{subject.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Student</label>
                <select
                  value={selectedStudent}
                  onChange={(e) => setSelectedStudent(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">All Students</option>
                  {filteredStudents.map(student => (
                    <option key={student.id} value={student.id}>
                      {student.first_name} {student.last_name}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview', icon: '📊' },
            { id: 'grades', name: 'Grade Records', icon: '📝' },
            { id: 'reports', name: 'Reports', icon: '📄' }
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
      {activeTab === 'overview' && analytics && (
        <div className="space-y-6">
          {/* Performance Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Average Score</h3>
              <p className="text-3xl font-bold text-blue-600">
                {analytics.average_score?.toFixed(1) || 0}%
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Highest Score</h3>
              <p className="text-3xl font-bold text-green-600">
                {analytics.highest_score?.toFixed(1) || 0}%
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Total Students</h3>
              <p className="text-3xl font-bold text-purple-600">
                {analytics.total_students || 0}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Pass Rate</h3>
              <p className="text-3xl font-bold text-orange-600">
                {analytics.pass_rate?.toFixed(1) || 0}%
              </p>
            </div>
          </div>

          {/* Performance Distribution */}
          {analytics.grade_distribution && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Grade Distribution</h3>
              <div className="grid grid-cols-5 gap-4">
                {Object.entries(analytics.grade_distribution).map(([grade, count]) => (
                  <div key={grade} className="text-center">
                    <div className={`w-full h-20 rounded-lg flex items-end justify-center ${
                      grade === 'A' || grade === 'A+' ? 'bg-green-200' :
                      grade === 'B' ? 'bg-blue-200' :
                      grade === 'C' ? 'bg-yellow-200' :
                      grade === 'D' ? 'bg-orange-200' :
                      'bg-red-200'
                    }`}>
                      <span className="text-lg font-bold pb-2">{count}</span>
                    </div>
                    <p className="text-sm font-medium mt-1">Grade {grade}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Subject Performance */}
          {analytics.subject_performance && (
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Subject Performance</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Subject
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Average
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Highest
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Lowest
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Students
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.entries(analytics.subject_performance).map(([subject, data]) => (
                      <tr key={subject} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {subject}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {data.average?.toFixed(1)}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {data.highest?.toFixed(1)}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {data.lowest?.toFixed(1)}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {data.student_count}
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
                      Student
                    </th>
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
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {grades.map((grade) => {
                    const gradeInfo = calculateGrade(grade.percentage);
                    const status = getPerformanceStatus(grade.percentage);
                    return (
                      <tr key={grade.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {grade.student?.first_name} {grade.student?.last_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {grade.student?.student_id}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {grade.subject?.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {grade.assessment_type}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {grade.score}/{grade.total_marks} ({grade.percentage?.toFixed(1)}%)
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`text-sm font-semibold ${gradeInfo.color}`}>
                            {gradeInfo.grade}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${status.color}`}>
                            {status.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(grade.assessment_date).toLocaleDateString()}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {grades.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500">No grades found for the selected criteria.</p>
            </div>
          )}
        </div>
      )}

      {/* Reports Tab */}
      {activeTab === 'reports' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Academic Reports</h3>
            <p className="text-gray-600 mb-6">
              Generate comprehensive reports for students and academic performance analysis.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2">Student Report Card</h4>
                <p className="text-sm text-gray-600 mb-4">
                  Generate detailed report cards with all subjects and grades.
                </p>
                {selectedStudent && (
                  <button 
                    onClick={generateReport}
                    className="btn btn-primary w-full"
                  >
                    Generate Report Card
                  </button>
                )}
                {!selectedStudent && (
                  <p className="text-sm text-gray-500">Select a student to generate report card</p>
                )}
              </div>
              
              <div className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2">Class Performance Report</h4>
                <p className="text-sm text-gray-600 mb-4">
                  Analyze class-wide performance and statistics.
                </p>
                <button className="btn btn-secondary w-full" disabled>
                  Coming Soon
                </button>
              </div>
              
              <div className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2">Subject Analysis</h4>
                <p className="text-sm text-gray-600 mb-4">
                  Detailed analysis of subject performance across all students.
                </p>
                <button className="btn btn-secondary w-full" disabled>
                  Coming Soon
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Grades;