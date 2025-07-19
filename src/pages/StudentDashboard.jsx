import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Helmet } from 'react-helmet';
import { BookOpen, Calendar, Trophy, TrendingUp, CheckCircle, XCircle, Clock, Target } from 'lucide-react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';

const StudentDashboard = () => {
  const { toast } = useToast();
  
  const [studentInfo] = useState({
    name: 'Alex Rodriguez',
    class: 'Grade 5A',
    rollNumber: 'STU001',
    teacher: 'Mr. Michael Chen',
    attendanceRate: 95,
    averageGrade: 87.5,
    rank: 3,
    totalStudents: 28
  });

  const [recentGrades] = useState([
    { id: 1, subject: 'Mathematics', grade: 92, maxGrade: 100, date: '2024-01-15', type: 'Test' },
    { id: 2, subject: 'English', grade: 88, maxGrade: 100, date: '2024-01-14', type: 'Assignment' },
    { id: 3, subject: 'Science', grade: 85, maxGrade: 100, date: '2024-01-12', type: 'Quiz' },
    { id: 4, subject: 'History', grade: 90, maxGrade: 100, date: '2024-01-10', type: 'Project' },
    { id: 5, subject: 'Art', grade: 95, maxGrade: 100, date: '2024-01-08', type: 'Portfolio' }
  ]);

  const [attendanceHistory] = useState([
    { date: '2024-01-15', status: 'present', day: 'Monday' },
    { date: '2024-01-14', status: 'present', day: 'Sunday' },
    { date: '2024-01-13', status: 'present', day: 'Saturday' },
    { date: '2024-01-12', status: 'absent', day: 'Friday' },
    { date: '2024-01-11', status: 'present', day: 'Thursday' },
    { date: '2024-01-10', status: 'present', day: 'Wednesday' },
    { date: '2024-01-09', status: 'present', day: 'Tuesday' }
  ]);

  const [upcomingEvents] = useState([
    { id: 1, title: 'Mathematics Test', date: '2024-01-18', type: 'exam' },
    { id: 2, title: 'Science Project Due', date: '2024-01-20', type: 'assignment' },
    { id: 3, title: 'Parent-Teacher Meeting', date: '2024-01-22', type: 'meeting' },
    { id: 4, title: 'Sports Day', date: '2024-01-25', type: 'event' }
  ]);

  const [achievements] = useState([
    { id: 1, title: 'Perfect Attendance', description: 'No absences this month', icon: Calendar, color: 'from-green-500 to-emerald-500' },
    { id: 2, title: 'Top Performer', description: 'Highest grade in Mathematics', icon: Trophy, color: 'from-yellow-500 to-orange-500' },
    { id: 3, title: 'Consistent Learner', description: 'Improved grades in all subjects', icon: TrendingUp, color: 'from-blue-500 to-indigo-500' },
    { id: 4, title: 'Class Rank #3', description: 'Top 3 in class performance', icon: Target, color: 'from-purple-500 to-violet-500' }
  ]);

  const StatCard = ({ title, value, icon: Icon, color, subtitle }) => (
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
              {subtitle && (
                <p className="text-white/60 text-sm mt-1">{subtitle}</p>
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
        <title>Student Dashboard - EduManage</title>
        <meta name="description" content="Student dashboard to view academic results, attendance records, and track personal progress in the school management system." />
      </Helmet>
      
      <Layout title="Student Dashboard">
        <div className="space-y-8">
          {/* Welcome Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center space-y-4"
          >
            <h1 className="text-4xl font-bold text-white">Welcome Back, {studentInfo.name}!</h1>
            <p className="text-white/70 text-lg">Track your academic progress and achievements</p>
          </motion.div>

          {/* Stats Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            <StatCard
              title="Average Grade"
              value={`${studentInfo.averageGrade}%`}
              icon={BookOpen}
              color="from-blue-500 to-indigo-500"
              subtitle="Excellent performance!"
            />
            <StatCard
              title="Attendance Rate"
              value={`${studentInfo.attendanceRate}%`}
              icon={Calendar}
              color="from-green-500 to-emerald-500"
              subtitle="Great attendance!"
            />
            <StatCard
              title="Class Rank"
              value={`#${studentInfo.rank}`}
              icon={Trophy}
              color="from-yellow-500 to-orange-500"
              subtitle={`Out of ${studentInfo.totalStudents} students`}
            />
            <StatCard
              title="Improvement"
              value="+5.2%"
              icon={TrendingUp}
              color="from-purple-500 to-violet-500"
              subtitle="This month"
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
                <TabsTrigger value="grades" className="text-white data-[state=active]:bg-white/20">My Grades</TabsTrigger>
                <TabsTrigger value="attendance" className="text-white data-[state=active]:bg-white/20">Attendance</TabsTrigger>
                <TabsTrigger value="achievements" className="text-white data-[state=active]:bg-white/20">Achievements</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                <div className="grid lg:grid-cols-2 gap-6">
                  {/* Student Profile */}
                  <Card className="glass-effect border-white/20">
                    <CardHeader>
                      <CardTitle className="text-white">My Profile</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex items-center space-x-4">
                        <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-violet-500 rounded-full flex items-center justify-center">
                          <span className="text-white font-bold text-xl">
                            {studentInfo.name.split(' ').map(n => n[0]).join('')}
                          </span>
                        </div>
                        <div>
                          <h3 className="text-white font-semibold text-lg">{studentInfo.name}</h3>
                          <p className="text-white/70">{studentInfo.class} • Roll: {studentInfo.rollNumber}</p>
                          <p className="text-white/60 text-sm">Class Teacher: {studentInfo.teacher}</p>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 pt-4">
                        <div className="text-center p-3 rounded-lg bg-white/5">
                          <p className="text-white/70 text-sm">Class Rank</p>
                          <p className="text-white font-semibold">#{studentInfo.rank}</p>
                        </div>
                        <div className="text-center p-3 rounded-lg bg-white/5">
                          <p className="text-white/70 text-sm">Average</p>
                          <p className="text-white font-semibold">{studentInfo.averageGrade}%</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Upcoming Events */}
                  <Card className="glass-effect border-white/20">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center">
                        <Clock className="h-5 w-5 mr-2" />
                        Upcoming Events
                      </CardTitle>
                      <CardDescription className="text-white/70">
                        Important dates and deadlines
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {upcomingEvents.map((event) => (
                        <div key={event.id} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                          <div>
                            <p className="text-white font-medium text-sm">{event.title}</p>
                            <p className="text-white/60 text-xs">{event.date}</p>
                          </div>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            event.type === 'exam' ? 'bg-red-500/20 text-red-400' :
                            event.type === 'assignment' ? 'bg-blue-500/20 text-blue-400' :
                            event.type === 'meeting' ? 'bg-purple-500/20 text-purple-400' :
                            'bg-green-500/20 text-green-400'
                          }`}>
                            {event.type}
                          </span>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="grades" className="space-y-6">
                <Card className="glass-effect border-white/20">
                  <CardHeader>
                    <CardTitle className="text-white">Academic Results</CardTitle>
                    <CardDescription className="text-white/70">
                      Your recent grades and performance across all subjects
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
                              <p className="text-white/60 text-sm">{grade.type} • {grade.date}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="flex items-center space-x-2">
                              <span className={`px-4 py-2 rounded-full text-lg font-bold ${
                                grade.grade >= 90 ? 'bg-green-500/20 text-green-400' :
                                grade.grade >= 80 ? 'bg-blue-500/20 text-blue-400' :
                                grade.grade >= 70 ? 'bg-yellow-500/20 text-yellow-400' :
                                'bg-red-500/20 text-red-400'
                              }`}>
                                {grade.grade}/{grade.maxGrade}
                              </span>
                            </div>
                            <p className="text-white/50 text-xs mt-1">
                              {Math.round((grade.grade / grade.maxGrade) * 100)}%
                            </p>
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
                    <CardTitle className="text-white">My Attendance Record</CardTitle>
                    <CardDescription className="text-white/70">
                      Your daily attendance history and statistics
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-6 grid md:grid-cols-3 gap-4">
                      <div className="text-center p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                        <p className="text-green-400 font-semibold text-lg">{studentInfo.attendanceRate}%</p>
                        <p className="text-white/70 text-sm">Overall Rate</p>
                      </div>
                      <div className="text-center p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
                        <p className="text-blue-400 font-semibold text-lg">
                          {attendanceHistory.filter(r => r.status === 'present').length}
                        </p>
                        <p className="text-white/70 text-sm">Days Present</p>
                      </div>
                      <div className="text-center p-4 rounded-lg bg-red-500/10 border border-red-500/20">
                        <p className="text-red-400 font-semibold text-lg">
                          {attendanceHistory.filter(r => r.status === 'absent').length}
                        </p>
                        <p className="text-white/70 text-sm">Days Absent</p>
                      </div>
                    </div>

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
                              <p className="text-white/60 text-sm">{record.day}</p>
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

              <TabsContent value="achievements" className="space-y-6">
                <Card className="glass-effect border-white/20">
                  <CardHeader>
                    <CardTitle className="text-white">My Achievements</CardTitle>
                    <CardDescription className="text-white/70">
                      Celebrate your academic milestones and accomplishments
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-2 gap-4">
                      {achievements.map((achievement) => {
                        const IconComponent = achievement.icon;
                        return (
                          <motion.div
                            key={achievement.id}
                            whileHover={{ scale: 1.02 }}
                            className="p-4 rounded-lg bg-white/5 hover:bg/white/10 transition-colors border border-white/10"
                          >
                            <div className="flex items-center space-x-4">
                              <div className={`w-12 h-12 bg-gradient-to-r ${achievement.color} rounded-lg flex items-center justify-center`}>
                                <IconComponent className="h-6 w-6 text-white" />
                              </div>
                              <div className="flex-1">
                                <h3 className="text-white font-semibold">{achievement.title}</h3>
                                <p className="text-white/70 text-sm">{achievement.description}</p>
                              </div>
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>

                    <div className="mt-8 text-center">
                      <Button 
                        onClick={() => handleFeatureClick('view-all-achievements')}
                        className="bg-gradient-to-r from-purple-500 to-violet-500 hover:from-purple-600 hover:to-violet-600"
                      >
                        View All Achievements
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

export default StudentDashboard;