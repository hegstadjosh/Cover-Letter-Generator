import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import {
  Description as ResumeIcon,
  Mail as CoverLetterIcon,
  Work as JobIcon,
  Person as BiographyIcon,
  Settings as SettingsIcon,
  Create as GeneratorIcon,
} from '@mui/icons-material';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { text: 'Resumes', path: '/resumes', icon: <ResumeIcon /> },
    { text: 'Cover Letters', path: '/cover-letters', icon: <CoverLetterIcon /> },
    { text: 'Job Descriptions', path: '/job-descriptions', icon: <JobIcon /> },
    { text: 'Biography', path: '/biography', icon: <BiographyIcon /> },
    { text: 'Generator', path: '/generator', icon: <GeneratorIcon /> },
    { text: 'Settings', path: '/settings', icon: <SettingsIcon /> },
  ];

  return (
    <AppBar position="sticky">
      <Toolbar>
        <Typography
          variant="h6"
          component="div"
          sx={{ cursor: 'pointer', mr: 4 }}
          onClick={() => navigate('/')}
        >
          Cover Letter Generator
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          {navItems.map((item) => (
            <Button
              key={item.path}
              color="inherit"
              startIcon={item.icon}
              onClick={() => navigate(item.path)}
              sx={{
                backgroundColor: location.pathname === item.path ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              }}
            >
              {item.text}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar; 