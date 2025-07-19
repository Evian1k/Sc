import React, { createContext, useContext, useState, useEffect } from 'react';
import { useToast } from "@/components/ui/use-toast";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Helper to get data from localStorage
const getInitialData = (key, defaultValue) => {
  try {
    const item = window.localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error(error);
    return defaultValue;
  }
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => getInitialData('currentUser', null));
  const [users, setUsers] = useState(() => getInitialData('users', []));
  const [studentsData, setStudentsData] = useState(() => getInitialData('studentsData', []));
  const [teachersData, setTeachersData] = useState(() => getInitialData('teachersData', []));
  const [feeStructures, setFeeStructures] = useState(() => getInitialData('feeStructures', []));
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  // Initialize with sample data if localStorage is empty
  useEffect(() => {
    if (localStorage.getItem('appInitialized') !== 'true') {
      const sampleUsers = [
        { id: 1, username: 'admin', password: 'admin123', role: 'admin', name: 'Dr. Sarah Johnson', email: 'admin@school.edu', loginCode: 'ADM001' },
        { id: 2, username: 'teacher1', password: 'teach123', role: 'teacher', name: 'Mr. Michael Chen', email: 'mchen@school.edu', loginCode: 'TCH001', assignedClass: 'Grade 5A', subject: 'Mathematics' },
        { id: 3, username: 'parent1', password: 'parent123', role: 'parent', name: 'Mrs. Emily Rodriguez', email: 'erodriguez@email.com', loginCode: 'PAR001' },
        { id: 4, username: 'student1', password: 'stud123', role: 'student', name: 'Alex Rodriguez', email: 'alex.rodriguez@student.edu', loginCode: 'STU001', class: 'Grade 5A', rollNumber: 'STU001', parentId: 3 }
      ];
      
      const sampleStudents = [
        { id: 4, name: 'Alex Rodriguez', class: 'Grade 5A', rollNumber: 'STU001', attendance: [], grades: {}, fees: { balance: 0, history: [] }, parentId: 3 },
        { id: 5, name: 'Emma Johnson', class: 'Grade 6B', rollNumber: 'STU002', attendance: [], grades: {}, fees: { balance: 250, history: [] }, parentId: null }
      ];
      
      const sampleTeachers = [
        { id: 2, name: 'Mr. Michael Chen', subject: 'Mathematics', class: 'Grade 5A' }
      ];

      const sampleFeeStructures = [
        { id: 1, className: 'Grade 5A', amount: 500, description: 'Monthly Tuition' },
        { id: 2, className: 'Grade 6B', amount: 550, description: 'Monthly Tuition' },
      ];

      setUsers(sampleUsers);
      setStudentsData(sampleStudents);
      setTeachersData(sampleTeachers);
      setFeeStructures(sampleFeeStructures);
      localStorage.setItem('appInitialized', 'true');
    }
    setLoading(false);
  }, []);

  // Persist state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('users', JSON.stringify(users));
  }, [users]);
  useEffect(() => {
    localStorage.setItem('studentsData', JSON.stringify(studentsData));
  }, [studentsData]);
  useEffect(() => {
    localStorage.setItem('teachersData', JSON.stringify(teachersData));
  }, [teachersData]);
  useEffect(() => {
    localStorage.setItem('feeStructures', JSON.stringify(feeStructures));
  }, [feeStructures]);
  useEffect(() => {
    localStorage.setItem('currentUser', JSON.stringify(user));
  }, [user]);

  const login = async (credentials) => {
    const { username, password, loginCode } = credentials;
    const foundUser = users.find(u => 
      (u.username === username || u.loginCode === loginCode) && u.password === password
    );

    if (foundUser) {
      const userSession = { ...foundUser };
      delete userSession.password;
      setUser(userSession);
      return { success: true, user: userSession };
    } else {
      return { success: false, error: 'Invalid credentials' };
    }
  };

  const logout = () => {
    setUser(null);
  };
  
  const generateUniqueCode = (prefix) => `${prefix}${Math.random().toString(36).substr(2, 6).toUpperCase()}`;

  const registerUser = (userData) => {
    const newUser = {
      ...userData,
      id: users.length > 0 ? Math.max(...users.map(u => u.id)) + 1 : 1,
      loginCode: generateUniqueCode(userData.role.slice(0, 3).toUpperCase())
    };
    
    setUsers(prevUsers => [...prevUsers, newUser]);

    if (newUser.role === 'student') {
      const newStudentData = {
        id: newUser.id,
        name: newUser.name,
        class: newUser.class,
        rollNumber: newUser.loginCode,
        attendance: [],
        grades: {},
        fees: { balance: 0, history: [] },
        parentId: newUser.parentId
      };
      setStudentsData(prev => [...prev, newStudentData]);
    } else if (newUser.role === 'teacher') {
       const newTeacherData = {
        id: newUser.id,
        name: newUser.name,
        subject: newUser.subject,
        class: newUser.assignedClass
      };
      setTeachersData(prev => [...prev, newTeacherData]);
    }

    toast({
      title: 'User Registered Successfully!',
      description: `${newUser.name} can now log in with the code: ${newUser.loginCode}`,
    });
    // Here you would trigger SMS/WhatsApp notification
    console.log(`Simulating SMS/WhatsApp notification for ${newUser.name} with login code: ${newUser.loginCode}`);

    return newUser;
  };
  
  const updateFeeStructure = (feeData) => {
    setFeeStructures(prev => {
        const existingIndex = prev.findIndex(f => f.id === feeData.id);
        if (existingIndex > -1) {
            const updated = [...prev];
            updated[existingIndex] = feeData;
            return updated;
        }
        const newFee = { ...feeData, id: feeStructures.length > 0 ? Math.max(...feeStructures.map(f => f.id)) + 1 : 1 };
        return [...prev, newFee];
    });
    toast({
      title: 'Fee Structure Updated!',
      description: `Fees for ${feeData.className} are now $${feeData.amount}.`
    });
  };

  const calculateFees = () => {
    setStudentsData(prevStudents => {
      return prevStudents.map(student => {
        const feeStructure = feeStructures.find(f => f.className === student.class);
        if (feeStructure) {
          const lastFeeEntry = student.fees.history[student.fees.history.length-1];
          const feeAlreadyCharged = lastFeeEntry && lastFeeEntry.description.includes(feeStructure.description);

          if (!feeAlreadyCharged) {
            const newBalance = (student.fees.balance || 0) + feeStructure.amount;
            const newHistoryEntry = {
              id: student.fees.history.length + 1,
              date: new Date().toISOString().split('T')[0],
              description: `${feeStructure.description} for ${student.class}`,
              amount: feeStructure.amount,
              type: 'debit'
            };
            
            console.log(`Simulating SMS/WhatsApp fee reminder for ${student.name}'s parent.`);

            return {
              ...student,
              fees: {
                balance: newBalance,
                history: [...student.fees.history, newHistoryEntry]
              }
            };
          }
        }
        return student;
      });
    });

     toast({
      title: 'Fees Calculated!',
      description: 'Student fee balances have been updated automatically.'
    });
  };


  const value = {
    user,
    users,
    studentsData,
    teachersData,
    feeStructures,
    login,
    logout,
    loading,
    registerUser,
    updateFeeStructure,
    calculateFees
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};