import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Edit3, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';

const GradesTab = ({ students, updateGrade, sendGradeSMS, classInfo }) => {
  const [editingStudentId, setEditingStudentId] = useState(null);
  const [gradeValue, setGradeValue] = useState('');

  const handleEdit = (student) => {
    setEditingStudentId(student.id);
    setGradeValue(student.grade);
  };

  const handleSave = (studentId) => {
    updateGrade(studentId, gradeValue);
    setEditingStudentId(null);
  };
  
  const handleKeyPress = (e, studentId) => {
    if (e.key === 'Enter') {
      handleSave(studentId);
    }
  };

  return (
    <Card className="glass-effect border-white/20">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-white">Grade Management</CardTitle>
          <CardDescription className="text-white/70">
            Update and manage student grades for {classInfo.className}
          </CardDescription>
        </div>
        <Button 
          onClick={sendGradeSMS}
          className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600"
        >
          Send Grades to Parents
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
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
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
                {editingStudentId === student.id ? (
                  <div className="flex items-center space-x-2">
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      value={gradeValue}
                      onChange={(e) => setGradeValue(e.target.value)}
                      className="w-20 bg-white/10 border-white/20 text-white"
                      onKeyPress={(e) => handleKeyPress(e, student.id)}
                    />
                    <Button
                      size="sm"
                      onClick={() => handleSave(student.id)}
                      className="bg-green-500 hover:bg-green-600"
                    >
                      <Save className="h-4 w-4" />
                    </Button>
                  </div>
                ) : (
                  <>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      student.grade >= 90 ? 'bg-green-500/20 text-green-400' :
                      student.grade >= 80 ? 'bg-blue-500/20 text-blue-400' :
                      student.grade >= 70 ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      {student.grade}%
                    </span>
                    <Button
                      size="sm"
                      variant="outline"
                      className="border-white/20 text-white hover:bg-white/10"
                      onClick={() => handleEdit(student)}
                    >
                      <Edit3 className="h-4 w-4 mr-1" />
                      Edit
                    </Button>
                  </>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default GradesTab;