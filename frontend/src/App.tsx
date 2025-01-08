import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box, CssBaseline } from '@mui/material';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Resumes from './pages/Resumes';
import CoverLetters from './pages/CoverLetters';
import JobDescriptions from './pages/JobDescriptions';
import Biography from './pages/Biography';
import Settings from './pages/Settings';
import Generator from './pages/Generator';

const App: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <CssBaseline />
      <Navbar />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/resumes" element={<Resumes />} />
          <Route path="/cover-letters" element={<CoverLetters />} />
          <Route path="/job-descriptions" element={<JobDescriptions />} />
          <Route path="/biography" element={<Biography />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/generator" element={<Generator />} />
        </Routes>
      </Box>
    </Box>
  );
};

export default App; 