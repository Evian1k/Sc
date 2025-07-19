import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Helmet } from 'react-helmet';
import { Users, GraduationCap, BookOpen, DollarSign, Calendar, TrendingUp, UserCheck, AlertCircle, MessageSquare } from 'lucide-react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const AdminDashboard = () => {
  const { toast } = useToast();
  const [stats] = useState({
    totalStudents: 1247,
    totalTeachers: 89,
    totalClasses: 42,
    pendingFees: 125000,
    attendanceRate: 94.2,
    averageGrade: 85.7
  });

  const [recentActivities] = useState([
    { id: 1, type: 'attendance', message: 'Grade 5A attendance marked by Mr. Chen', time: '2 hours ago' },
    { id: 2, type: 'grade', message: 'Mathematics grades updated for Grade 7B', time: '4 hours ago' },
    { id: 3, type: 'fee', message: 'Fee payment received from Alex Rodriguez', time: '6 hours ago' },
    { id: 4, type: 'sms', message: 'Attendance SMS sent to 45 parents', time: '8 hours ago' }
  ]);

  const [students] = useState([
    { id: 1, name: 'Alex Rodriguez', class: 'Grade 5A', attendance: 95, fees: 'Paid', lastSeen: '2024-01-15' },
    { id: 2, name: 'Emma Johnson', class: 'Grade 6B', attendance: 88, fees: 'Pending', lastSeen: '2024-01-15' },
    { id: 3, name: 'Michael Chen', class: 'Grade 7A', attendance: 92, fees: 'Paid', lastSeen: '2024-01-14' },
    { id: 4, name: 'Sarah Wilson', class: 'Grade 5A', attendance: 97, fees: 'Paid', lastSeen: '2024-01-15' }
  ]);

  const [teachers] = useState([
    { id: 1, name: 'Mr. Michael Chen', subject: 'Mathematics', class: 'Grade 5A', students: 28 },
    { id: 2, name: 'Ms. Sarah Davis', subject: 'English', class: 'Grade 6B', students: 25 },
    { id: 3, name: 'Dr. James Wilson', subject: 'Science', class: 'Grade 7A', students: 30 },
    { id: 4, name: 'Mrs. Lisa Brown', subject: 'History', class: 'Grade 8C', students: 27 }
  ]);

  const StatCard = ({ title, value, icon: Icon, color, change }) => (
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
              {change && (
                <p className="text-green-400 text-sm flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  {change}
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

  const AddStudentForm = () => (
    <DialogContent className="glass-effect border-white/20 text-white">
      <DialogHeader>
        <DialogTitle>Add New Student</DialogTitle>
        <DialogDescription className="text-white/70">
          Enter the new student's details below. A unique login code will be generated automatically.
        </DialogDescription>
      </DialogHeader>
      <div className="grid gap-4 py-4">
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="name" className="text-right">Name</Label>
          <Input id="name" className="col-span-3 bg-white/10 border-white/20 text-white" />
        </div>
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="class" className="text-right">Class</Label>
          <Input id="class" className="col-span-3 bg-white/10 border-white/20 text-white" />
        </div>
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="parent" className="text-right">Parent's Name</Label>
          <Input id="parent" className="col-span-3 bg-white/10 border-white/20 text-white" />
        </div>
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="contact" className="text-right">Parent's Contact</Label>
          <Input id="contact" className="col-span-3 bg-white/10 border-white/20 text-white" />
        </div>
      </div>
       <Button onClick={() => handleFeatureClick('add-student-submit')} className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600">
        Add Student
      </Button>
    </DialogContent>
  );

  return (
    <>
      <Helmet>
        <title>Admin Dashboard - EduManage</title>
        <meta name="description" content="Administrator dashboard for comprehensive school management including students, teachers, attendance, grades, and fees." />
      </Helmet>
      
      <Layout title="Administrator Dashboard">
        <div className="space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center space-y-4"
          >
            <h1 className="text-4xl font-bold text-white">Welcome Back, Administrator</h1>
            <p className="text-white/70 text-lg">Manage your school with comprehensive oversight and control</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            <StatCard
              title="Total Students"
              value={stats.totalStudents.toLocaleString()}
              icon={GraduationCap}
              color="from-blue-500 to-indigo-500"
              change="+12 this month"
            />
            <StatCard
              title="Total Teachers"
              value={stats.totalTeachers}
              icon={Users}
              color="from-green-500 to-emerald-500"
              change="+3 this month"
            />
            <StatCard
              title="Active Classes"
              value={stats.totalClasses}
              icon={BookOpen}
              color="from-purple-500 to-violet-500"
            />
            <StatCard
              title="Pending Fees"
              value={`${stats.pendingFees.toLocaleString()}`}
              icon={DollarSign}
              color="from-red-500 to-pink-500"
              change="-8% this month"
            />
            <StatCard
              title="Attendance Rate"
              value={`${stats.attendanceRate}%`}
              icon={UserCheck}
              color="from-orange-500 to-amber-500"
              change="+2.1% this month"
            />
            <StatCard
              title="Broadcast Messages"
              value="Send"
              icon={MessageSquare}
              color="from-cyan-500 to-blue-500"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Tabs defaultValue="overview" className="space-y-6">
              <TabsList className="glass-effect border-white/20 grid w-full grid-cols-5">
                <TabsTrigger value="overview" className="text-white data-[state=active]:bg-white/20">Overview</TabsTrigger>
                <TabsTrigger value="students" className="text-white data-[state=active]:bg-white/20">Students</TabsTrigger>
                <TabsTrigger value="teachers" className="text-white data-[state=active]:bg-white/20">Teachers</TabsTrigger>
                <TabsTrigger value="attendance" className="text-white data-[state=active]:bg-white/20">Attendance</TabsTrigger>
                <TabsTrigger value="fees" className="text-white data-[state=active]:bg-white/20">Fees</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                <div className="grid lg:grid-cols-2 gap-6">
                  <Card className="glass-effect border-white/20">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center">
                        <Calendar className="h-5 w-5 mr-2" />
                        Recent Activities
                      </CardTitle>
                      <CardDescription className="text-white/70">
                        Latest system activities and updates
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {recentActivities.map((activity) => (
                        <div key={activity.id} className="flex items-start space-x-3 p-3 rounded-lg bg-white/5">
                          <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                          <div className="flex-1">
                            <p className="text-white text-sm">{activity.message}</p>
                            <p className="text-white/50 text-xs">{activity.time}</p>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>

                  <Card className="glass-effect border-white/20">
                    <CardHeader>
                      <CardTitle className="text-white">Quick Actions</CardTitle>
                      <CardDescription className="text-white/70">
                        Frequently used administrative functions
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button className="w-full justify-start bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600">
                            <GraduationCap className="h-4 w-4 mr-2" />
                            Add New Student / Generate Login Code
                          </Button>
                        </DialogTrigger>
                        <AddStudentForm />
                      </Dialog>
                      <Button 
                        className="w-full justify-start bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600"
                        onClick={() => handleFeatureClick('add-teacher')}
                      >
                        <Users className="h-4 w-4 mr-2" />
                        Add New Teacher / Assign User
                      </Button>
                      <Button 
                        className="w-full justify-start bg-gradient-to-r from-purple-500 to-violet-500 hover:from-purple-600 hover:to-violet-600"
                        onClick={() => handleFeatureClick('send-sms')}
                      >
                        <AlertCircle className="h-4 w-4 mr-2" />
                        Send SMS Notifications
                      </Button>
                      <Button 
                        className="w-full justify-start bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600"
                        onClick={() => handleFeatureClick('generate-report')}
                      >
                        <TrendingUp className="h-4 w-4 mr-2" />
                        Generate Reports
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="students" className="space-y-6">
                <Card className="glass-effect border-white/20">
                  <CardHeader>
                    <CardTitle className="text-white">Student Management</CardTitle>
                    <CardDescription className="text-white/70">
                      View and manage all students in the system
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {students.map((student) => (
                        <div key={student.id} className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                          <div className="flex items-center space-x-4">
                            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-violet-500 rounded-full flex items-center justify-center">
                              <span className="text-white font-semibold text-sm">
                                {student.name.split(' ').map(n => n[0]).join('')}
                              </span>
                            </div>
                            <div>
                              <p className="text-white font-medium">{student.name}</p>
                              <p className="text-white/60 text-sm">{student.class}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-6 text-sm">
                            <div className="text-center">
                              <p className="text-white/60">Attendance</p>
                              <p className="text-white font-medium">{student.attendance}%</p>
                            </div>
                            <div className="text-center">
                              <p className="text-white/60">Fees</p>
                              <p className={`font-medium ${student.fees === 'Paid' ? 'text-green-400' : 'text-red-400'}`}>
                                {student.fees}
                              </p>
                            </div>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="border-white/20 text-white hover:bg-white/10"
                              onClick={() => handleFeatureClick('view-student')}
                            >
                              View Details
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="teachers" className="space-y-6">
                <Card className="glass-effect border-white/20">
                  <CardHeader>
                    <CardTitle className="text-white">Teacher Management</CardTitle>
                    <CardDescription className="text-white/70">
                      View and manage all teachers in the system
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {teachers.map((teacher) => (
                        <div key={teacher.id} className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                          <div className="flex items-center space-x-4">
                            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                              <span className="text-white font-semibold text-sm">
                                {teacher.name.split(' ').map(n => n[0]).join('')}
                              </span>
                            </div>
                            <div>
                              <p className="text-white font-medium">{teacher.name}</p>
                              <p className="text-white/60 text-sm">{teacher.subject} • {teacher.class}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-6 text-sm">
                            <div className="text-center">
                              <p className="text-white/60">Students</p>
                              <p className="text-white font-medium">{teacher.students}</p>
                            </div>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="border-white/20 text-white hover:bg-white/10"
                              onClick={() => handleFeatureClick('view-teacher')}
                            >
                              View Details
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="attendance" className="space-y-6">
                <Card className="glass-effect border-white/20">
                  <CardHeader>
                    <CardTitle className="text-white">Attendance Overview</CardTitle>
                    <CardDescription className="text-white/70">
                      Monitor attendance across all classes and students
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center py-12">
                      <UserCheck className="h-16 w-16 text-white/50 mx-auto mb-4" />
                      <p className="text-white/70 text-lg">Attendance management interface</p>
                      <Button 
                        className="mt-4 bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600"
                        onClick={() => handleFeatureClick('attendance-management')}
                      >
                        View Detailed Attendance
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="fees" className="space-y-6">
                <Card className="glass-effect border-white/20">
                  <CardHeader>
                    <CardTitle className="text-white">Fee Management</CardTitle>
                    <CardDescription className="text-white/70">
                      Track and manage student fee payments
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center py-12">
                      <DollarSign className="h-16 w-16 text-white/50 mx-auto mb-4" />
                      <p className="text-white/70 text-lg">Fee management interface</p>
                      <Button 
                        className="mt-4 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600"
                        onClick={() => handleFeatureClick('fee-management')}
                      >
                        Manage Fees
                      </Button>
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

export default AdminDashboard;