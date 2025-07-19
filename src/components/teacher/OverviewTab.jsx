import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';

const OverviewTab = ({ recentActivities, classInfo }) => {
  return (
    <div className="grid lg:grid-cols-2 gap-6">
      <Card className="glass-effect border-white/20">
        <CardHeader>
          <CardTitle className="text-white">Recent Activities</CardTitle>
          <CardDescription className="text-white/70">
            Your recent teaching activities
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
          <CardTitle className="text-white">Class Summary</CardTitle>
          <CardDescription className="text-white/70">
            Overview of your assigned class
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-white/70">Class Name:</span>
              <span className="text-white font-medium">{classInfo.className}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-white/70">Subject:</span>
              <span className="text-white font-medium">{classInfo.subject}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-white/70">Total Students:</span>
              <span className="text-white font-medium">{classInfo.totalStudents}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-white/70">Average Grade:</span>
              <span className="text-white font-medium">{classInfo.averageGrade}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-white/70">Today's Attendance:</span>
              <span className="text-white font-medium">
                {classInfo.presentToday}/{classInfo.totalStudents}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default OverviewTab;