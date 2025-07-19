import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';

const Navbar = () => {
  const { user, role } = useAuth();
  const navigate = useNavigate();

  const handleDashboardRedirect = () => {
    if (user && role) {
      navigate(`/${role}`);
    } else {
      navigate('/login');
    }
  };

  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="fixed top-0 left-0 right-0 z-50 glass-effect border-b border-white/10"
    >
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">E</span>
          </div>
          <span className="text-2xl font-bold text-white">EduManage</span>
        </Link>
        <nav className="hidden md:flex items-center space-x-6">
          <Link to="/" className="text-white/80 hover:text-white transition-colors">Home</Link>
          <Link to="/contact" className="text-white/80 hover:text-white transition-colors">Contact</Link>
        </nav>
        <div className="flex items-center space-x-4">
          {user ? (
            <Button
              onClick={handleDashboardRedirect}
              className="bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 transition-all transform hover:scale-105"
            >
              Go to Dashboard
            </Button>
          ) : (
            <>
              <Button variant="ghost" className="text-white hover:bg-white/10" onClick={() => navigate('/login')}>
                Login
              </Button>
              <Button
                onClick={() => navigate('/login')}
                className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105"
              >
                Register
              </Button>
            </>
          )}
        </div>
      </div>
    </motion.header>
  );
};

export default Navbar;