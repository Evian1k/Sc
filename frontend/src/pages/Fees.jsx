import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Fees = () => {
  const { user } = useAuth();
  const [fees, setFees] = useState([]);
  const [students, setStudents] = useState([]);
  const [feeStructures, setFeeStructures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedFee, setSelectedFee] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // overview, fees, payments, structure
  const [analytics, setAnalytics] = useState(null);
  const [formData, setFormData] = useState({
    student_id: '',
    fee_structure_id: '',
    amount: '',
    due_date: '',
    academic_year: new Date().getFullYear(),
    term: '1',
    fee_type: 'Tuition',
    description: ''
  });
  const [paymentData, setPaymentData] = useState({
    amount_paid: '',
    payment_method: 'Cash',
    payment_date: new Date().toISOString().split('T')[0],
    reference_number: '',
    notes: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [feesRes, studentsRes, analyticsRes] = await Promise.all([
        api.get('/fees'),
        api.get('/students'),
        api.get('/fees/analytics')
      ]);
      
      setFees(feesRes.data.fees || []);
      setStudents(studentsRes.data.students || []);
      setAnalytics(analyticsRes.data.analytics);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFee = async (e) => {
    e.preventDefault();
    try {
      if (selectedFee) {
        await api.put(`/fees/${selectedFee.id}`, formData);
      } else {
        await api.post('/fees', formData);
      }
      setShowAddModal(false);
      setSelectedFee(null);
      resetFormData();
      fetchData();
    } catch (error) {
      console.error('Error saving fee:', error);
      alert('Error saving fee. Please try again.');
    }
  };

  const handleSubmitPayment = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/fees/${selectedFee.id}/payment`, paymentData);
      setShowPaymentModal(false);
      setSelectedFee(null);
      resetPaymentData();
      fetchData();
      alert('Payment recorded successfully!');
    } catch (error) {
      console.error('Error recording payment:', error);
      alert('Error recording payment. Please try again.');
    }
  };

  const resetFormData = () => {
    setFormData({
      student_id: '',
      fee_structure_id: '',
      amount: '',
      due_date: '',
      academic_year: new Date().getFullYear(),
      term: '1',
      fee_type: 'Tuition',
      description: ''
    });
  };

  const resetPaymentData = () => {
    setPaymentData({
      amount_paid: '',
      payment_method: 'Cash',
      payment_date: new Date().toISOString().split('T')[0],
      reference_number: '',
      notes: ''
    });
  };

  const handleEdit = (fee) => {
    setSelectedFee(fee);
    setFormData({ ...fee });
    setShowAddModal(true);
  };

  const handlePayment = (fee) => {
    setSelectedFee(fee);
    setPaymentData({
      ...paymentData,
      amount_paid: (fee.amount - fee.amount_paid).toString()
    });
    setShowPaymentModal(true);
  };

  const sendFeeReminder = async (feeId) => {
    try {
      await api.post(`/notifications/fee/reminder`, {
        student_id: fees.find(f => f.id === feeId)?.student_id,
        amount_due: fees.find(f => f.id === feeId)?.amount - fees.find(f => f.id === feeId)?.amount_paid,
        due_date: fees.find(f => f.id === feeId)?.due_date
      });
      alert('Fee reminder sent successfully!');
    } catch (error) {
      console.error('Error sending reminder:', error);
      alert('Error sending reminder. Please try again.');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount);
  };

  const getPaymentStatus = (fee) => {
    const paidPercentage = (fee.amount_paid / fee.amount) * 100;
    if (paidPercentage >= 100) return 'Paid';
    if (paidPercentage > 0) return 'Partial';
    if (new Date(fee.due_date) < new Date()) return 'Overdue';
    return 'Pending';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Paid': return 'bg-green-100 text-green-800';
      case 'Partial': return 'bg-yellow-100 text-yellow-800';
      case 'Overdue': return 'bg-red-100 text-red-800';
      default: return 'bg-blue-100 text-blue-800';
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
          <h1 className="text-2xl font-bold text-gray-900">Fee Management</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage student fees, payments, and financial tracking
          </p>
        </div>
        {(user?.role === 'admin' || user?.role === 'accountant') && (
          <button
            onClick={() => setShowAddModal(true)}
            className="btn btn-primary"
          >
            Add New Fee
          </button>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview', icon: '📊' },
            { id: 'fees', name: 'Fee Records', icon: '💰' },
            { id: 'payments', name: 'Payment History', icon: '💳' },
            { id: 'structure', name: 'Fee Structure', icon: '📋' }
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
          {/* Financial Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Total Fees Due</h3>
              <p className="text-3xl font-bold text-blue-600">
                {formatCurrency(analytics.total_fees_due || 0)}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Total Collected</h3>
              <p className="text-3xl font-bold text-green-600">
                {formatCurrency(analytics.total_fees_collected || 0)}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Outstanding</h3>
              <p className="text-3xl font-bold text-red-600">
                {formatCurrency(analytics.total_outstanding || 0)}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Collection Rate</h3>
              <p className="text-3xl font-bold text-purple-600">
                {analytics.collection_rate?.toFixed(1) || 0}%
              </p>
            </div>
          </div>

          {/* Recent Payments */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Payments</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Student
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Method
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {analytics.recent_payments?.slice(0, 5).map((payment) => (
                    <tr key={payment.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {payment.student_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(payment.amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(payment.payment_date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {payment.payment_method}
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
                      Student
                    </th>
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
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {fees.map((fee) => {
                    const status = getPaymentStatus(fee);
                    const balance = fee.amount - fee.amount_paid;
                    return (
                      <tr key={fee.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {fee.student?.first_name} {fee.student?.last_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {fee.student?.student_id}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
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
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(status)}`}>
                            {status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            {balance > 0 && (
                              <button
                                onClick={() => handlePayment(fee)}
                                className="text-green-600 hover:text-green-900"
                              >
                                Pay
                              </button>
                            )}
                            {(user?.role === 'admin' || user?.role === 'accountant') && (
                              <>
                                <button
                                  onClick={() => handleEdit(fee)}
                                  className="text-indigo-600 hover:text-indigo-900"
                                >
                                  Edit
                                </button>
                                {balance > 0 && (
                                  <button
                                    onClick={() => sendFeeReminder(fee.id)}
                                    className="text-blue-600 hover:text-blue-900"
                                  >
                                    Remind
                                  </button>
                                )}
                              </>
                            )}
                          </div>
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

      {/* Add/Edit Fee Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-2/3 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {selectedFee ? 'Edit Fee' : 'Add New Fee'}
              </h3>
              <form onSubmit={handleSubmitFee} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Student</label>
                    <select
                      value={formData.student_id}
                      onChange={(e) => setFormData({ ...formData, student_id: e.target.value })}
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
                    <label className="block text-sm font-medium text-gray-700">Fee Type</label>
                    <select
                      value={formData.fee_type}
                      onChange={(e) => setFormData({ ...formData, fee_type: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    >
                      <option value="Tuition">Tuition</option>
                      <option value="Transport">Transport</option>
                      <option value="Meals">Meals</option>
                      <option value="Books">Books</option>
                      <option value="Uniform">Uniform</option>
                      <option value="Exam">Exam Fee</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Amount (KES)</label>
                    <input
                      type="number"
                      value={formData.amount}
                      onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                      min="0"
                      step="0.01"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Due Date</label>
                    <input
                      type="date"
                      value={formData.due_date}
                      onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Academic Year</label>
                    <input
                      type="number"
                      value={formData.academic_year}
                      onChange={(e) => setFormData({ ...formData, academic_year: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Term</label>
                    <select
                      value={formData.term}
                      onChange={(e) => setFormData({ ...formData, term: e.target.value })}
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
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows="3"
                  />
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddModal(false);
                      setSelectedFee(null);
                      resetFormData();
                    }}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    {selectedFee ? 'Update' : 'Add'} Fee
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Payment Modal */}
      {showPaymentModal && selectedFee && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Record Payment - {selectedFee.student?.first_name} {selectedFee.student?.last_name}
              </h3>
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <p><strong>Fee Type:</strong> {selectedFee.fee_type}</p>
                <p><strong>Total Amount:</strong> {formatCurrency(selectedFee.amount)}</p>
                <p><strong>Amount Paid:</strong> {formatCurrency(selectedFee.amount_paid)}</p>
                <p><strong>Balance:</strong> {formatCurrency(selectedFee.amount - selectedFee.amount_paid)}</p>
              </div>
              <form onSubmit={handleSubmitPayment} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Amount to Pay (KES)</label>
                    <input
                      type="number"
                      value={paymentData.amount_paid}
                      onChange={(e) => setPaymentData({ ...paymentData, amount_paid: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                      min="0"
                      max={selectedFee.amount - selectedFee.amount_paid}
                      step="0.01"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Payment Method</label>
                    <select
                      value={paymentData.payment_method}
                      onChange={(e) => setPaymentData({ ...paymentData, payment_method: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    >
                      <option value="Cash">Cash</option>
                      <option value="Bank Transfer">Bank Transfer</option>
                      <option value="Mobile Money">Mobile Money</option>
                      <option value="Cheque">Cheque</option>
                      <option value="Card">Card</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Payment Date</label>
                    <input
                      type="date"
                      value={paymentData.payment_date}
                      onChange={(e) => setPaymentData({ ...paymentData, payment_date: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Reference Number</label>
                    <input
                      type="text"
                      value={paymentData.reference_number}
                      onChange={(e) => setPaymentData({ ...paymentData, reference_number: e.target.value })}
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                      placeholder="Optional"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Notes</label>
                  <textarea
                    value={paymentData.notes}
                    onChange={(e) => setPaymentData({ ...paymentData, notes: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows="3"
                    placeholder="Optional payment notes"
                  />
                </div>
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowPaymentModal(false);
                      setSelectedFee(null);
                      resetPaymentData();
                    }}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Record Payment
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

export default Fees;