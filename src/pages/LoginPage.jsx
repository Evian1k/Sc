import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { Eye, EyeOff, GraduationCap, Users, BookOpen, Shield } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';

const LoginPage = () => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: '',
    loginCode: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await login(credentials);
      if (result.success) {
        toast({
          title: "Login successful!",
          description: `Welcome back, ${result.user.name}!`,
        });
        
        // Redirect based on role
        const roleRoutes = {
          admin: '/admin',
          teacher: '/teacher',
          parent: '/parent',
          student: '/student'
        };
        navigate(roleRoutes[result.user.role] || '/');
      } else {
        toast({
          title: "Login failed",
          description: result.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Login error",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  const demoCredentials = [
    { role: 'Admin', username: 'admin', password: 'admin123', code: 'ADM001', icon: Shield, color: 'from-red-500 to-pink-500' },
    { role: 'Teacher', username: 'teacher1', password: 'teach123', code: 'TCH001', icon: BookOpen, color: 'from-blue-500 to-indigo-500' },
    { role: 'Parent', username: 'parent1', password: 'parent123', code: 'PAR001', icon: Users, color: 'from-green-500 to-emerald-500' },
    { role: 'Student', username: 'student1', password: 'stud123', code: 'STU001', icon: GraduationCap, color: 'from-purple-500 to-violet-500' }
  ];

  const fillDemoCredentials = (demo) => {
    setCredentials({
      username: demo.username,
      password: demo.password,
      loginCode: demo.code
    });
  };

  return (
    <>
      <Helmet>
        <title>Login - EduManage School Management System</title>
        <meta name="description" content="Secure login portal for administrators, teachers, parents, and students to access the school management system." />
      </Helmet>
      
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-8 items-center">
          {/* Left Side - Login Form */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Card className="glass-effect border-white/20 shadow-2xl">
              <CardHeader className="text-center space-y-4">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: "spring" }}
                  className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center"
                >
                  <GraduationCap className="h-8 w-8 text-white" />
                </motion.div>
                <CardTitle className="text-3xl font-bold text-white">Welcome to EduManage</CardTitle>
                <CardDescription className="text-white/70">
                  Sign in to access your school management dashboard
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="username" className="text-white">Username</Label>
                    <Input
                      id="username"
                      name="username"
                      type="text"
                      value={credentials.username}
                      onChange={handleInputChange}
                      className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                      placeholder="Enter your username"
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-white">Password</Label>
                    <div className="relative">
                      <Input
                        id="password"
                        name="password"
                        type={showPassword ? "text" : "password"}
                        value={credentials.password}
                        onChange={handleInputChange}
                        className="bg-white/10 border-white/20 text-white placeholder:text-white/50 pr-10"
                        placeholder="Enter your password"
                        required
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="absolute right-0 top-0 h-full px-3 text-white/70 hover:text-white hover:bg-transparent"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="loginCode" className="text-white">Login Code (Optional)</Label>
                    <Input
                      id="loginCode"
                      name="loginCode"
                      type="text"
                      value={credentials.loginCode}
                      onChange={handleInputChange}
                      className="bg-white/10 border-white/20 text-white placeholder:text-white/50"
                      placeholder="Enter your login code"
                    />
                  </div>

                  <Button
                    type="submit"
                    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold py-2 px-4 rounded-lg transition-all duration-300 transform hover:scale-105"
                    disabled={loading}
                  >
                    {loading ? "Signing in..." : "Sign In"}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </motion.div>

          {/* Right Side - Demo Credentials */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="space-y-6"
          >
            <div className="text-center space-y-2">
              <h2 className="text-2xl font-bold text-white">Demo Accounts</h2>
              <p className="text-white/70">Click any card below to auto-fill login credentials</p>
            </div>

            <div className="grid gap-4">
              {demoCredentials.map((demo, index) => {
                const IconComponent = demo.icon;
                return (
                  <motion.div
                    key={demo.role}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 + index * 0.1 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card 
                      className="glass-effect border-white/20 cursor-pointer card-hover"
                      onClick={() => fillDemoCredentials(demo)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center space-x-4">
                          <div className={`w-12 h-12 bg-gradient-to-r ${demo.color} rounded-lg flex items-center justify-center`}>
                            <IconComponent className="h-6 w-6 text-white" />
                          </div>
                          <div className="flex-1">
                            <h3 className="font-semibold text-white">{demo.role}</h3>
                            <p className="text-sm text-white/60">Code: {demo.code}</p>
                          </div>
                          <div className="text-right text-sm text-white/50">
                            <p>Click to login</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="text-center space-y-4"
            >
              <div className="glass-effect border-white/20 rounded-lg p-4">
                <h3 className="font-semibold text-white mb-2">System Features</h3>
                <div className="grid grid-cols-2 gap-2 text-sm text-white/70">
                  <div>• Role-based Access</div>
                  <div>• Attendance Tracking</div>
                  <div>• Grade Management</div>
                  <div>• Fee Management</div>
                  <div>• SMS Notifications</div>
                  <div>• Mobile Responsive</div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </>
  );
};

export default LoginPage;