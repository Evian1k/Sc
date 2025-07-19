import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';

const AttendanceTab = ({ students, toggleAttendance, sendAttendanceSMS, classInfo, selectedDate }) => {
  return (
    <Card className="glass-effect border-white/20">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-white">Digital Attendance Register</CardTitle>
          <CardDescription className="text-white/70">
            Mark attendance for {classInfo.className} - {selectedDate}
          </CardDescription>
        </div>
        <Button 
          onClick={sendAttendanceSMS}
          className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600"
        >
          Send SMS to Parents
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {students.map((student) => (
            <motion.div
              key={student.id}
              whileHover={{ scale: 1.01 }}
              className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-violet-500 rounded-full flex items-center justify-center">
                  <span className="text-white font-semibold text-sm">
                    {student.name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <div>
                  <p className="text-white font-medium">{student.name}</p>
                  <p className="text-white/60 text-sm">Roll: {student.rollNumber}</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  student.attendance === 'present' 
                    ? 'bg-green-500/20 text-green-400' 
                    : 'bg-red-500/20 text-red-400'
                }`}>
                  {student.attendance === 'present' ? 'Present' : 'Absent'}
                </span>
                <Button
                  size="sm"
                  variant="outline"
                  className="border-white/20 text-white hover:bg-white/10"
                  onClick={() => toggleAttendance(student.id)}
                >
                  {student.attendance === 'present' ? (
                    <XCircle className="h-4 w-4 mr-1" />
                  ) : (
                    <CheckCircle className="h-4 w-4 mr-1" />
                  )}
                  Mark {student.attendance === 'present' ? 'Absent' : 'Present'}
                </Button>
              </div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default AttendanceTab;