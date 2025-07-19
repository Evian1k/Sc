import React from 'react';
import { motion } from 'framer-motion';
import { Helmet } from 'react-helmet';
import { useNavigate, Link } from 'react-router-dom';
import { GraduationCap, Users, BookOpen, ChevronRight, Mail, Phone, MapPin } from 'lucide-react';
import Navbar from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const HomePage = () => {
  const navigate = useNavigate();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 100,
      },
    },
  };

  const FeatureCard = ({ icon, title, description }) => (
    <motion.div variants={itemVariants}>
      <Card className="glass-effect text-center h-full border-white/10 hover:border-white/30 transition-all card-hover">
        <CardHeader>
          <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mb-4">
            {icon}
          </div>
          <CardTitle className="text-white text-xl">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-white/70">{description}</p>
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <>
      <Helmet>
        <title>Welcome to EduManage - Smart School Management</title>
        <meta name="description" content="EduManage is a modern, all-in-one school management system designed to streamline administrative tasks and enhance communication." />
      </Helmet>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white overflow-x-hidden">
        <Navbar />

        {/* Hero Section */}
        <motion.section
          className="container mx-auto px-4 pt-40 pb-20 text-center"
          initial="hidden"
          animate="visible"
          variants={containerVariants}
        >
          <motion.h1
            className="text-5xl md:text-7xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400"
            variants={itemVariants}
          >
            The Future of School Management
          </motion.h1>
          <motion.p className="mt-6 text-lg md:text-xl text-white/80 max-w-3xl mx-auto" variants={itemVariants}>
            EduManage provides a seamless, integrated platform for administrators, teachers, parents, and students to collaborate and succeed.
          </motion.p>
          <motion.div className="mt-10 flex justify-center space-x-4" variants={itemVariants}>
            <Button
              size="lg"
              className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105"
              onClick={() => navigate('/login')}
            >
              Get Started <ChevronRight className="ml-2 h-5 w-5" />
            </Button>
            <Button size="lg" variant="outline" className="text-white border-white/50 hover:bg-white/10" onClick={() => navigate('/contact')}>
              Contact Us
            </Button>
          </motion.div>
        </motion.section>

        {/* Features Section */}
        <motion.section
          className="py-20"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={containerVariants}
        >
          <div className="container mx-auto px-4">
            <motion.h2 className="text-4xl font-bold text-center mb-12" variants={itemVariants}>
              Everything You Need in One Place
            </motion.h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              <FeatureCard
                icon={<GraduationCap className="w-8 h-8 text-white" />}
                title="Student Management"
                description="Keep track of student records, attendance, and performance with ease."
              />
              <FeatureCard
                icon={<Users className="w-8 h-8 text-white" />}
                title="Teacher & Parent Portals"
                description="Dedicated dashboards for teachers and parents to stay informed and connected."
              />
              <FeatureCard
                icon={<BookOpen className="w-8 h-8 text-white" />}
                title="Academic Tools"
                description="Manage grades, subjects, and classes effortlessly with our intuitive tools."
              />
            </div>
          </div>
        </motion.section>
        
        {/* Call to Action */}
        <motion.section
          className="py-20 bg-white/5"
           initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.5 }}
          variants={itemVariants}
        >
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to Transform Your School?</h2>
            <p className="text-white/70 mb-8 max-w-2xl mx-auto">Join hundreds of institutions revolutionizing their management processes with EduManage.</p>
            <Button
              size="lg"
              className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 transition-all transform hover:scale-105"
              onClick={() => navigate('/login')}
            >
              Request a Demo
            </Button>
          </div>
        </motion.section>
        
        {/* Footer */}
        <footer className="py-12">
            <div className="container mx-auto px-4 text-center text-white/60">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
                    <div className="space-y-2">
                        <h3 className="text-lg font-semibold text-white">Contact Us</h3>
                        <p className="flex items-center justify-center"><Mail className="w-4 h-4 mr-2" /> contact@edumanage.com</p>
                        <p className="flex items-center justify-center"><Phone className="w-4 h-4 mr-2" /> (123) 456-7890</p>
                    </div>
                    <div className="space-y-2">
                        <h3 className="text-lg font-semibold text-white">Our Location</h3>
                        <p className="flex items-center justify-center"><MapPin className="w-4 h-4 mr-2" /> 123 Education Lane, Learning City, 12345</p>
                    </div>
                    <div className="space-y-2">
                        <h3 className="text-lg font-semibold text-white">Quick Links</h3>
                        <div className="flex justify-center space-x-4">
                           <Link to="/" className="hover:text-white transition-colors">Home</Link>
                           <Link to="/contact" className="hover:text-white transition-colors">Contact</Link>
                           <Link to="/login" className="hover:text-white transition-colors">Login</Link>
                        </div>
                    </div>
                </div>
                <p>&copy; {new Date().getFullYear()} EduManage. All Rights Reserved.</p>
            </div>
        </footer>
      </div>
    </>
  );
};

export default HomePage;