import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Helmet } from 'react-helmet';
import { GraduationCap, Calendar, DollarSign, BookOpen, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';

const ParentDashboard = () => {
  const { toast } = useToast();
  
  const [childInfo] = useState({
    name: 'Alex Rodriguez',
    class: 'Grade 5A',
    rollNumber: 'STU001',
    teacher: 'Mr. Michael Chen',
    attendanceRate: 95,
    averageGrade: 87.5,
    feeBalance: 0,
    nextFeeDate: '2024-02-15'
  });

  const [recentGrades] = useState([
    { id: 1, subject: 'Mathematics', grade: 92, date: '2024-01-15', teacher: 'Mr. Michael Chen' },
    { id: 2, subject: 'English', grade: 88, date: '2024-01-14', teacher: 'Ms. Sarah Davis' },
    { id: 3, subject: 'Science', grade: 85, date: '2024-01-12', teacher: 'Dr. James Wilson' },
    { id: 4, subject: 'History', grade: 90, date: '2024-01-10', teacher: 'Mrs. Lisa Brown' }
  ]);

  const [attendanceHistory] = useState([
    { date: '2024-01-15', status: 'present' },
    { date: '2024-01-14', status: 'present' },
    { date: '2024-01-13', status: 'present' },
    { date: '2024-01-12', status: 'absent' },
    { date: '2024-01-11', status: 'present' },
    { date: '2024-01-10', status: 'present' },
    { date: '2024-01-09', status: 'present' }
  ]);

  const [notifications] = useState([
    { id: 1, type: 'attendance', message: 'Alex was marked present today', time: '2 hours ago', read: false },
    { id: 2, type: 'grade', message: 'New Mathematics grade posted: 92%', time: '1 day ago', read: false },
    { id: 3, type: 'fee', message: 'Fee payment confirmation received', time: '3 days ago', read: true },
    { id: 4, type: 'general', message: 'Parent-teacher meeting scheduled', time: '5 days ago', read: true }
  ]);

  const [feeHistory] = useState([
    { id: 1, description: 'Tuition Fee - January 2024', amount: 500, status: 'Paid', date: '2024-01-01' },
    { id: 2, description: 'Activity Fee - January 2024', amount: 50, status: 'Paid', date: '2024-01-01' },
    { id: 3, description: 'Library Fee - January 2024', amount: 25, status: 'Paid', date: '2024-01-01' },
    { id: 4, description: 'Tuition Fee - February 2024', amount: 500, status: 'Pending', date: '2024-02-01' }
  ]);

  const StatCard = ({ title, value, icon: Icon, color, status }) => (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card className="glass-effect border-white/20 card-hover">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/70 text-sm font-medium">{title}</p>
              <p className="text-2xl font-bold text-white">{value}</p>
              {status && (
                <p className={`text-sm mt-1 ${status === 'good' ? 'text-green-400' : status === 'warning' ? 'text-yellow-400' : 'text-red-400'}`}>
                  {status === 'good' ? 'Excellent' : status === 'warning' ? 'Needs Attention' : 'Critical'}
                </p>
              )}
            </div>
            <div className={`w-12 h-12 bg-gradient-to-r ${color} rounded-lg flex items-center justify-center`}>
              <Icon className="h-6 w-6 text-white" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  const handleFeatureClick = (feature) => {
    toast({
      title: "🚧 This feature isn't implemented yet—but don't worry! You can request it in your next prompt! 🚀"
    });
  };

  return (
    <>
      <Helmet>
        <title>Parent Dashboard - EduManage</title>
        <meta name="description" content="Parent dashboard to monitor child's academic progress, attendance, grades, and fee payments in the school management system." />
      </Helmet>
      
      <Layout title="Parent Dashboard">
        <div className="space-y-8">
          {/* Welcome Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center space-y-4"
          >
            <h1 className="text-4xl font-bold text-white">Welcome, Mrs. Rodriguez</h1>
            <p className="text-white/70 text-lg">Monitor {childInfo.name}'s academic progress and school activities</p>
          </motion.div>

          {/* Stats Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            <StatCard
              title="Attendance Rate"
              value={`${childInfo.attendanceRate}%`}
              icon={Calendar}
              color="from-green-500 to-emerald-500"
              status="good"
            />
            <StatCard
              title="Average Grade"
              value={`${childInfo.averageGrade}%`}
              icon={BookOpen}
              color="from-blue-500 to-indigo-500"
              status="good"
            />
            <StatCard
              title="Fee Balance"
              value={childInfo.feeBalance === 0 ? 'Paid' : `$${childInfo.feeBalance}`}
              icon={DollarSign}
              color={childInfo.feeBalance === 0 ? "from-green-500 to-emerald-500" : "from-red-500 to-pink-500"}
              status={childInfo.feeBalance === 0 ? "good" : "warning"}
            />
            <StatCard
              title="Class Rank"
              value="3rd"
              icon={GraduationCap}
              color="from-purple-500 to-violet-500"
              status="good"
            />
          </motion.div>

          {/* Main Content Tabs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Tabs defaultValue="overview" className="space-y-6">
              <TabsList className="glass-effect border-white/20 grid w-full grid-cols-4">
                <TabsTrigger value="overview" className="text-white data-[state=active]:bg-white/20">Overview</TabsTrigger>
                <TabsTrigger value="grades" className="text-white data-[state=active]:bg-white/20">Grades</TabsTrigger>
                <TabsTrigger value="attendance" className="text-white data-[state=active]:bg-white/20">Attendance</TabsTrigger>
                <TabsTrigger value="fees" className="text-white data-[state=active]:bg-white/20">Fees</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                <div className="grid lg:grid-cols-2 gap-6">
                  {/* Child Information */}
                  <Card className="glass-effect border-white/20">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center">
                        <GraduationCap className="h-5 w-5 mr-2" />
                        Student Information
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex items-center space-x-4">
                        <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-violet-500 rounded-full flex items-center justify-center">
                          <span className="text-white font-bold text-xl">
                            {childInfo.name.split(' ').map(n => n[0]).join('')}
                          </span>
                        </div>
                        <div>
                          <h3 className="text-white font-semibold text-lg">{childInfo.name}</h3>
                          <p className="text-white/70">{childInfo.class} • Roll: {childInfo.rollNumber}</p>
                          <p className="text-white/60 text-sm">Class Teacher: {childInfo.teacher}</p>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 pt-4">
                        <div className="text-center p-3 rounded-lg bg-white/5">
                          <p className="text-white/70 text-sm">Attendance</p>
                          <p className="text-white font-semibold">{childInfo.attendanceRate}%</p>
                        </div>
                        <div className="text-center p-3 rounded-lg bg-white/5">
                          <p className="text-white/70 text-sm">Average Grade</p>
                          <p className="text-white font-semibold">{childInfo.averageGrade}%</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Recent Notifications */}
                  <Card className="glass-effect border-white/20">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center">
                        <AlertCircle className="h-5 w-5 mr-2" />
                        Recent Notifications
                      </CardTitle>
                      <CardDescription className="text-white/70">
                        Latest updates about your child
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {notifications.slice(0, 4).map((notification) => (
                        <div key={notification.id} className={`flex items-start space-x-3 p-3 rounded-lg ${notification.read ? 'bg-white/5' : 'bg-blue-500/10 border border-blue-500/20'}`}>
                          <div className={`w-2 h-2 rounded-full mt-2 ${notification.read ? 'bg-white/30' : 'bg-blue-500'}`}></div>
                          <div className="flex-1">
                            <p className="text-white text-sm">{notification.message}</p>
                            <p className="text-white/50 text-xs">{notification.time}</p>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="grades" className="space-y-6">
                <Card className="glass-effect border-white/20">
                  <CardHeader>
                    <CardTitle className="text-white">Academic Performance</CardTitle>
                    <CardDescription className="text-white/70">
                      Recent grades and academic progress for {childInfo.name}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {recentGrades.map((grade) => (
                        <motion.div
                          key={grade.id}
                          whileHover={{ scale: 1.01 }}
                          className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                        >
                          <div className="flex items-center space-x-4">
                            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                              <BookOpen className="h-5 w-5 text-white" />
                            </div>
                            <div>
                              <p className="text-white font-medium">{grade.subject}</p>
                              <p className="text-white/60 text-sm">Teacher: {grade.teacher}</p>
                              <p className="text-white/50 text-xs">{grade.date}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className={`px-4 py-2 rounded-full text-lg font-bold ${
                              grade.grade >= 90 ? 'bg-green-500/20 text-green-400' :
                              grade.grade >= 80 ? 'bg-blue-500/20 text-blue-400' :
                              grade.grade >= 70 ? 'bg-yellow-500/20 text-yellow-400' :
                              'bg-red-500/20 text-red-400'
                            }`}>
                              {grade.grade}%
                            </span>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="attendance" className="space-y-6">
                <Card className="glass-effect border-white/20">
                  <CardHeader>
                    <CardTitle className="text-white">Attendance History</CardTitle>
                    <CardDescription className="text-white/70">
                      Daily attendance record for {childInfo.name}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {attendanceHistory.map((record, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="flex items-center justify-between p-4 rounded-lg bg-white/5"
                        >
                          <div className="flex items-center space-x-4">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                              record.status === 'present' 
                                ? 'bg-green-500/20' 
                                : 'bg-red-500/20'
                            }`}>
                              {record.status === 'present' ? (
                                <CheckCircle className="h-5 w-5 text-green-400" />
                              ) : (
                                <XCircle className="h-5 w-5 text-red-400" />
                              )}
                            </div>
                            <div>
                              <p className="text-white font-medium">{record.date}</p>
                              <p className="text-white/60 text-sm">
                                {new Date(record.date).toLocaleDateString('en-US', { weekday: 'long' })}
                              </p>
                            </div>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                            record.status === 'present' 
                              ? 'bg-green-500/20 text-green-400' 
                              : 'bg-red-500/20 text-red-400'
                          }`}>
                            {record.status === 'present' ? 'Present' : 'Absent'}
                          </span>
                        </motion.div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="fees" className="space-y-6">
                <Card className="glass-effect border-white/20">
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                      <CardTitle className="text-white">Fee Management</CardTitle>
                      <CardDescription className="text-white/70">
                        Track fee payments and outstanding balances
                      </CardDescription>
                    </div>
                    <Button 
                      onClick={() => handleFeatureClick('pay-fees')}
                      className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600"
                    >
                      Pay Fees Online
                    </Button>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* Fee Summary */}
                      <div className="grid md:grid-cols-3 gap-4 mb-6">
                        <div className="text-center p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                          <p className="text-green-400 font-semibold text-lg">$0</p>
                          <p className="text-white/70 text-sm">Outstanding Balance</p>
                        </div>
                        <div className="text-center p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
                          <p className="text-blue-400 font-semibold text-lg">$575</p>
                          <p className="text-white/70 text-sm">Paid This Month</p>
                        </div>
                        <div className="text-center p-4 rounded-lg bg-purple-500/10 border border-purple-500/20">
                          <p className="text-purple-400 font-semibold text-lg">{childInfo.nextFeeDate}</p>
                          <p className="text-white/70 text-sm">Next Due Date</p>
                        </div>
                      </div>

                      {/* Fee History */}
                      <div className="space-y-3">
                        <h3 className="text-white font-semibold mb-3">Payment History</h3>
                        {feeHistory.map((fee) => (
                          <div key={fee.id} className="flex items-center justify-between p-4 rounded-lg bg-white/5">
                            <div>
                              <p className="text-white font-medium">{fee.description}</p>
                              <p className="text-white/60 text-sm">{fee.date}</p>
                            </div>
                            <div className="text-right">
                              <p className="text-white font-semibold">${fee.amount}</p>
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                fee.status === 'Paid' 
                                  ? 'bg-green-500/20 text-green-400' 
                                  : 'bg-yellow-500/20 text-yellow-400'
                              }`}>
                                {fee.status}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </motion.div>
        </div>
      </Layout>
    </>
  );
};

export default ParentDashboard;