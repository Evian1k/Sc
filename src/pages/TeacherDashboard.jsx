import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Helmet } from 'react-helmet';
import { Users, BookOpen, Calendar, CheckCircle } from 'lucide-react';
import Layout from '@/components/Layout';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import AttendanceTab from '@/components/teacher/AttendanceTab';
import GradesTab from '@/components/teacher/GradesTab';
import OverviewTab from '@/components/teacher/OverviewTab';

const TeacherDashboard = () => {
  const { toast } = useToast();
  const [selectedDate] = useState(new Date().toISOString().split('T')[0]);
  
  const [classInfo, setClassInfo] = useState({
    className: 'Grade 5A',
    subject: 'Mathematics',
    totalStudents: 28,
    presentToday: 26,
    averageGrade: 87.5
  });

  const [students, setStudents] = useState([
    { id: 1, name: 'Alex Rodriguez', rollNumber: 'STU001', attendance: 'present', grade: 85 },
    { id: 2, name: 'Emma Johnson', rollNumber: 'STU002', attendance: 'present', grade: 92 },
    { id: 3, name: 'Michael Chen', rollNumber: 'STU003', attendance: 'absent', grade: 78 },
    { id: 4, name: 'Sarah Wilson', rollNumber: 'STU004', attendance: 'present', grade: 95 },
    { id: 5, name: 'David Brown', rollNumber: 'STU005', attendance: 'present', grade: 88 },
    { id: 6, name: 'Lisa Davis', rollNumber: 'STU006', attendance: 'present', grade: 91 }
  ]);

  const [recentActivities] = useState([
    { id: 1, message: 'Attendance marked for today', time: '2 hours ago' },
    { id: 2, message: 'Grades updated for Unit Test 3', time: '1 day ago' },
    { id: 3, message: 'SMS notifications sent to parents', time: '2 days ago' },
    { id: 4, message: 'Assignment grades posted', time: '3 days ago' }
  ]);

  const toggleAttendance = (studentId) => {
    setStudents(currentStudents => 
      currentStudents.map(student => 
        student.id === studentId 
          ? { ...student, attendance: student.attendance === 'present' ? 'absent' : 'present' }
          : student
      )
    );
    toast({
      title: "Attendance Updated",
      description: "Student attendance has been marked successfully.",
    });
  };

  const updateGrade = (studentId, newGrade) => {
    const grade = parseInt(newGrade);
    if (isNaN(grade) || grade < 0 || grade > 100) {
      toast({
        title: "Invalid Grade",
        description: "Please enter a grade between 0 and 100.",
        variant: "destructive"
      });
      return;
    }
    setStudents(currentStudents => 
      currentStudents.map(student => 
        student.id === studentId ? { ...student, grade } : student
      )
    );
    toast({
      title: "Grade Updated",
      description: "Student grade has been updated successfully.",
    });
  };

  const sendAttendanceSMS = () => {
    toast({
      title: "SMS Notifications Sent",
      description: "Attendance notifications have been sent to all parents.",
    });
  };

  const sendGradeSMS = () => {
    toast({
      title: "Grade Notifications Sent",
      description: "Grade updates have been sent to all parents.",
    });
  };

  const StatCard = ({ title, value, icon: Icon, color }) => (
    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
      <Card className="glass-effect border-white/20 card-hover">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/70 text-sm font-medium">{title}</p>
              <p className="text-2xl font-bold text-white">{value}</p>
            </div>
            <div className={`w-12 h-12 bg-gradient-to-r ${color} rounded-lg flex items-center justify-center`}>
              <Icon className="h-6 w-6 text-white" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <>
      <Helmet>
        <title>Teacher Dashboard - EduManage</title>
        <meta name="description" content="Teacher dashboard for managing class attendance, grades, and student progress in the school management system." />
      </Helmet>
      
      <Layout title="Teacher Dashboard">
        <div className="space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center space-y-4"
          >
            <h1 className="text-4xl font-bold text-white">Welcome Back, Mr. Chen</h1>
            <p className="text-white/70 text-lg">Manage your class {classInfo.className} - {classInfo.subject}</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            <StatCard title="Total Students" value={classInfo.totalStudents} icon={Users} color="from-blue-500 to-indigo-500" />
            <StatCard title="Present Today" value={classInfo.presentToday} icon={CheckCircle} color="from-green-500 to-emerald-500" />
            <StatCard title="Class Average" value={`${classInfo.averageGrade}%`} icon={BookOpen} color="from-purple-500 to-violet-500" />
            <StatCard title="Attendance Rate" value={`${Math.round((classInfo.presentToday / classInfo.totalStudents) * 100)}%`} icon={Calendar} color="from-orange-500 to-amber-500" />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Tabs defaultValue="attendance" className="space-y-6">
              <TabsList className="glass-effect border-white/20 grid w-full grid-cols-3">
                <TabsTrigger value="attendance" className="text-white data-[state=active]:bg-white/20">Attendance</TabsTrigger>
                <TabsTrigger value="grades" className="text-white data-[state=active]:bg-white/20">Grades</TabsTrigger>
                <TabsTrigger value="overview" className="text-white data-[state=active]:bg-white/20">Overview</TabsTrigger>
              </TabsList>

              <TabsContent value="attendance">
                <AttendanceTab students={students} toggleAttendance={toggleAttendance} sendAttendanceSMS={sendAttendanceSMS} classInfo={classInfo} selectedDate={selectedDate} />
              </TabsContent>
              <TabsContent value="grades">
                <GradesTab students={students} updateGrade={updateGrade} sendGradeSMS={sendGradeSMS} classInfo={classInfo} />
              </TabsContent>
              <TabsContent value="overview">
                <OverviewTab recentActivities={recentActivities} classInfo={classInfo} />
              </TabsContent>
            </Tabs>
          </motion.div>
        </div>
      </Layout>
    </>
  );
};

export default TeacherDashboard;