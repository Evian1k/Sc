import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Exams = () => {
  const { user } = useAuth();
  const [exams, setExams] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [classes, setClasses] = useState([]);
  const [students, setStudents] = useState([]);
  const [examResults, setExamResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('exams'); // exams, schedule, results, analytics
  const [showExamModal, setShowExamModal] = useState(false);
  const [showResultModal, setShowResultModal] = useState(false);
  const [selectedExam, setSelectedExam] = useState(null);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  
  const [examForm, setExamForm] = useState({
    name: '',
    description: '',
    exam_type: 'Mid-term',
    academic_year: new Date().getFullYear(),
    term: '1',
    start_date: '',
    end_date: '',
    total_marks: 100,
    passing_marks: 50,
    instructions: '',
    rules: ''
  });

  const [resultForm, setResultForm] = useState({
    exam_id: '',
    student_id: '',
    subject_id: '',
    class_id: '',
    marks_obtained: '',
    total_marks: 100,
    remarks: '',
    teacher_comments: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
             const [examsRes, subjectsRes, classesRes] = await Promise.all([
         api.get('/exams'),
         api.get('/classes/subjects'),
         api.get('/classes')
       ]);
      
      setExams(examsRes.data.exams || []);
      setSubjects(subjectsRes.data.subjects || []);
      setClasses(classesRes.data.classes || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchExamResults = async (examId) => {
    try {
      const response = await api.get(`/exams/${examId}/results`);
      setExamResults(response.data.results || []);
    } catch (error) {
      console.error('Error fetching exam results:', error);
    }
  };

  const fetchAnalytics = async (examId) => {
    try {
      const response = await api.get(`/exams/${examId}/analytics`);
      setAnalytics(response.data.analytics);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const handleCreateExam = async (e) => {
    e.preventDefault();
    try {
      if (selectedExam) {
        await api.put(`/exams/${selectedExam.id}`, examForm);
      } else {
        await api.post('/exams', examForm);
      }
      setShowExamModal(false);
      setSelectedExam(null);
      resetExamForm();
      fetchData();
      alert('Exam saved successfully!');
    } catch (error) {
      console.error('Error saving exam:', error);
      alert('Error saving exam. Please try again.');
    }
  };

  const handleSubmitResult = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/exams/${resultForm.exam_id}/results`, resultForm);
      setShowResultModal(false);
      resetResultForm();
      if (resultForm.exam_id) {
        fetchExamResults(resultForm.exam_id);
      }
      alert('Result saved successfully!');
    } catch (error) {
      console.error('Error saving result:', error);
      alert('Error saving result. Please try again.');
    }
  };

  const publishExam = async (examId) => {
    try {
      await api.post(`/exams/${examId}/publish`);
      fetchData();
      alert('Exam published successfully!');
    } catch (error) {
      console.error('Error publishing exam:', error);
      alert('Error publishing exam. Please try again.');
    }
  };

  const publishResults = async (examId) => {
    try {
      await api.post(`/exams/${examId}/results/publish`);
      fetchData();
      fetchExamResults(examId);
      alert('Results published successfully!');
    } catch (error) {
      console.error('Error publishing results:', error);
      alert('Error publishing results. Please try again.');
    }
  };

  const resetExamForm = () => {
    setExamForm({
      name: '',
      description: '',
      exam_type: 'Mid-term',
      academic_year: new Date().getFullYear(),
      term: '1',
      start_date: '',
      end_date: '',
      total_marks: 100,
      passing_marks: 50,
      instructions: '',
      rules: ''
    });
  };

  const resetResultForm = () => {
    setResultForm({
      exam_id: '',
      student_id: '',
      subject_id: '',
      class_id: '',
      marks_obtained: '',
      total_marks: 100,
      remarks: '',
      teacher_comments: ''
    });
  };

  const handleEditExam = (exam) => {
    setSelectedExam(exam);
    setExamForm({ ...exam });
    setShowExamModal(true);
  };

  const handleAddResult = (exam) => {
    setResultForm({ ...resultForm, exam_id: exam.id });
    setShowResultModal(true);
  };

  const calculateGrade = (percentage) => {
    if (percentage >= 80) return 'A';
    if (percentage >= 70) return 'B';
    if (percentage >= 60) return 'C';
    if (percentage >= 50) return 'D';
    return 'F';
  };

  const getGradeColor = (grade) => {
    switch (grade) {
      case 'A': return 'text-green-600';
      case 'B': return 'text-blue-600';
      case 'C': return 'text-yellow-600';
      case 'D': return 'text-orange-600';
      default: return 'text-red-600';
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
          <h1 className="text-2xl font-bold text-gray-900">Exam Management</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage exams, schedules, results, and performance analytics
          </p>
        </div>
        {(user?.role === 'admin' || user?.role === 'teacher') && (
          <button
            onClick={() => setShowExamModal(true)}
            className="btn btn-primary"
          >
            Create New Exam
          </button>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'exams', name: 'Exams', icon: '📝' },
            { id: 'schedule', name: 'Schedule', icon: '📅' },
            { id: 'results', name: 'Results', icon: '📊' },
            { id: 'analytics', name: 'Analytics', icon: '📈' }
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

      {/* Exams Tab */}
      {activeTab === 'exams' && (
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Exam List</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Exam Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Academic Year
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Term
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date Range
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {exams.map((exam) => (
                    <tr key={exam.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{exam.name}</div>
                        <div className="text-sm text-gray-500">{exam.description}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {exam.exam_type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {exam.academic_year}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        Term {exam.term}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(exam.start_date).toLocaleDateString()} - {new Date(exam.end_date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          exam.is_published 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {exam.is_published ? 'Published' : 'Draft'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleEditExam(exam)}
                            className="text-indigo-600 hover:text-indigo-900"
                          >
                            Edit
                          </button>
                          {!exam.is_published && (user?.role === 'admin') && (
                            <button
                              onClick={() => publishExam(exam.id)}
                              className="text-green-600 hover:text-green-900"
                            >
                              Publish
                            </button>
                          )}
                          <button
                            onClick={() => {
                              setSelectedExam(exam);
                              fetchExamResults(exam.id);
                              setActiveTab('results');
                            }}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Results
                          </button>
                          <button
                            onClick={() => {
                              setSelectedExam(exam);
                              fetchAnalytics(exam.id);
                              setActiveTab('analytics');
                            }}
                            className="text-purple-600 hover:text-purple-900"
                          >
                            Analytics
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Results Tab */}
      {activeTab === 'results' && (
        <div className="space-y-6">
          {selectedExam && (
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    Exam Results: {selectedExam.name}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {selectedExam.exam_type} - {selectedExam.academic_year} Term {selectedExam.term}
                  </p>
                </div>
                <div className="flex space-x-2">
                  {(user?.role === 'admin' || user?.role === 'teacher') && (
                    <button
                      onClick={() => handleAddResult(selectedExam)}
                      className="btn btn-primary"
                    >
                      Add Result
                    </button>
                  )}
                  {!selectedExam.results_published && user?.role === 'admin' && examResults.length > 0 && (
                    <button
                      onClick={() => publishResults(selectedExam.id)}
                      className="btn btn-success"
                    >
                      Publish Results
                    </button>
                  )}
                </div>
              </div>

              {examResults.length > 0 ? (
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
                          Marks
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Percentage
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Grade
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {examResults.map((result) => {
                        const grade = calculateGrade(result.percentage);
                        return (
                          <tr key={result.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">
                                {result.student?.first_name} {result.student?.last_name}
                              </div>
                              <div className="text-sm text-gray-500">
                                {result.student?.student_id}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {result.subject?.name}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {result.marks_obtained}/{result.total_marks}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {result.percentage?.toFixed(1)}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`text-sm font-semibold ${getGradeColor(grade)}`}>
                                {grade}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                result.percentage >= selectedExam.passing_marks
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-red-100 text-red-800'
                              }`}>
                                {result.percentage >= selectedExam.passing_marks ? 'Pass' : 'Fail'}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500">No results available for this exam.</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && analytics && selectedExam && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Analytics: {selectedExam.name}
            </h3>
            
            {/* Overall Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="text-sm font-medium text-blue-800">Total Students</h4>
                <p className="text-2xl font-bold text-blue-600">
                  {analytics.overall_statistics?.total_students || 0}
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="text-sm font-medium text-green-800">Average Score</h4>
                <p className="text-2xl font-bold text-green-600">
                  {analytics.overall_statistics?.average_score?.toFixed(1) || 0}%
                </p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="text-sm font-medium text-purple-800">Pass Rate</h4>
                <p className="text-2xl font-bold text-purple-600">
                  {analytics.overall_statistics?.pass_rate?.toFixed(1) || 0}%
                </p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <h4 className="text-sm font-medium text-orange-800">Highest Score</h4>
                <p className="text-2xl font-bold text-orange-600">
                  {analytics.overall_statistics?.highest_score?.toFixed(1) || 0}%
                </p>
              </div>
            </div>

            {/* Grade Distribution */}
            {analytics.grade_distribution && (
              <div className="mb-6">
                <h4 className="text-md font-medium text-gray-900 mb-3">Grade Distribution</h4>
                <div className="grid grid-cols-5 gap-4">
                  {Object.entries(analytics.grade_distribution).map(([grade, count]) => (
                    <div key={grade} className="text-center">
                      <div className={`w-full h-20 rounded-lg flex items-end justify-center ${
                        grade === 'A' ? 'bg-green-200' :
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
              <div>
                <h4 className="text-md font-medium text-gray-900 mb-3">Subject Performance</h4>
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
                            {data.students_count}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Create/Edit Exam Modal */}
      {showExamModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-2/3 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {selectedExam ? 'Edit Exam' : 'Create New Exam'}
              </h3>
              <form onSubmit={handleCreateExam} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Exam Name</label>
                    <input
                      type="text"
                      value={examForm.name}
                      onChange={(e) => setExamForm({ ...examForm, name: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Exam Type</label>
                    <select
                      value={examForm.exam_type}
                      onChange={(e) => setExamForm({ ...examForm, exam_type: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    >
                      <option value="Mid-term">Mid-term</option>
                      <option value="Final">Final</option>
                      <option value="Quiz">Quiz</option>
                      <option value="Assignment">Assignment</option>
                      <option value="Project">Project</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Academic Year</label>
                    <input
                      type="number"
                      value={examForm.academic_year}
                      onChange={(e) => setExamForm({ ...examForm, academic_year: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Term</label>
                    <select
                      value={examForm.term}
                      onChange={(e) => setExamForm({ ...examForm, term: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    >
                      <option value="1">Term 1</option>
                      <option value="2">Term 2</option>
                      <option value="3">Term 3</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Start Date</label>
                    <input
                      type="date"
                      value={examForm.start_date}
                      onChange={(e) => setExamForm({ ...examForm, start_date: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">End Date</label>
                    <input
                      type="date"
                      value={examForm.end_date}
                      onChange={(e) => setExamForm({ ...examForm, end_date: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Total Marks</label>
                    <input
                      type="number"
                      value={examForm.total_marks}
                      onChange={(e) => setExamForm({ ...examForm, total_marks: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                      min="1"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Passing Marks</label>
                    <input
                      type="number"
                      value={examForm.passing_marks}
                      onChange={(e) => setExamForm({ ...examForm, passing_marks: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                      min="1"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    value={examForm.description}
                    onChange={(e) => setExamForm({ ...examForm, description: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows="3"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Instructions</label>
                  <textarea
                    value={examForm.instructions}
                    onChange={(e) => setExamForm({ ...examForm, instructions: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows="3"
                    placeholder="Instructions for students..."
                  />
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowExamModal(false);
                      setSelectedExam(null);
                      resetExamForm();
                    }}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    {selectedExam ? 'Update' : 'Create'} Exam
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Add Result Modal */}
      {showResultModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Add Exam Result</h3>
              <form onSubmit={handleSubmitResult} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Student</label>
                    <select
                      value={resultForm.student_id}
                      onChange={(e) => {
                        const student = students.find(s => s.id == e.target.value);
                        setResultForm({ 
                          ...resultForm, 
                          student_id: e.target.value,
                          class_id: student?.class_id || ''
                        });
                      }}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    >
                      <option value="">Select Student</option>
                      {students.map(student => (
                        <option key={student.id} value={student.id}>
                          {student.first_name} {student.last_name} ({student.student_id})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Subject</label>
                    <select
                      value={resultForm.subject_id}
                      onChange={(e) => setResultForm({ ...resultForm, subject_id: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    >
                      <option value="">Select Subject</option>
                      {subjects.map(subject => (
                        <option key={subject.id} value={subject.id}>
                          {subject.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Marks Obtained</label>
                    <input
                      type="number"
                      value={resultForm.marks_obtained}
                      onChange={(e) => setResultForm({ ...resultForm, marks_obtained: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                      min="0"
                      max={resultForm.total_marks}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Total Marks</label>
                    <input
                      type="number"
                      value={resultForm.total_marks}
                      onChange={(e) => setResultForm({ ...resultForm, total_marks: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                      min="1"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Teacher Comments</label>
                  <textarea
                    value={resultForm.teacher_comments}
                    onChange={(e) => setResultForm({ ...resultForm, teacher_comments: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows="3"
                    placeholder="Optional comments about student performance..."
                  />
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowResultModal(false);
                      resetResultForm();
                    }}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Save Result
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

export default Exams;