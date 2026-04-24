import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AnimatePresence, motion } from 'framer-motion';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import TenderLibrary from './pages/TenderLibrary';
import Analytics from './pages/Analytics';
import LandingPage from './pages/LandingPage';

const App = () => {
  const [isActive, setIsActive] = useState(false);

  const handleStart = () => {
    setIsActive(true);
  };

  return (
    <Router>
      <Toaster position="top-right" />
      <AnimatePresence mode="wait">
        {!isActive ? (
          <motion.div
            key="landing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <LandingPage onStart={handleStart} />
          </motion.div>
        ) : (
          <motion.div
            key="app"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="min-h-screen bg-gray-50"
          >
            <Layout onLogout={() => setIsActive(false)}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard/:tenderId" element={<Dashboard />} />
                <Route path="/tenders" element={<TenderLibrary />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Layout>
          </motion.div>
        )}
      </AnimatePresence>
    </Router>
  );
};

export default App;
