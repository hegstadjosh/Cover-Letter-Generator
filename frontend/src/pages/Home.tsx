import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Box,
} from '@mui/material';
import {
  Description as ResumeIcon,
  Mail as CoverLetterIcon,
  Work as JobIcon,
  Create as GeneratorIcon,
} from '@mui/icons-material';

const Home: React.FC = () => {
  const navigate = useNavigate();

  const quickActions = [
    {
      title: 'Upload Resume',
      description: 'Add a new resume to your collection',
      icon: <ResumeIcon sx={{ fontSize: 40 }} />,
      action: () => navigate('/resumes'),
    },
    {
      title: 'Create Cover Letter',
      description: 'Generate a new cover letter using AI',
      icon: <CoverLetterIcon sx={{ fontSize: 40 }} />,
      action: () => navigate('/generator'),
    },
    {
      title: 'Add Job Description',
      description: 'Save a new job description',
      icon: <JobIcon sx={{ fontSize: 40 }} />,
      action: () => navigate('/job-descriptions'),
    },
    {
      title: 'View Cover Letters',
      description: 'Browse your generated cover letters',
      icon: <GeneratorIcon sx={{ fontSize: 40 }} />,
      action: () => navigate('/cover-letters'),
    },
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 8 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Welcome to Cover Letter Generator
        </Typography>
        <Typography variant="h6" color="textSecondary" paragraph>
          Create personalized cover letters using AI technology. Upload your resume, add job descriptions,
          and generate tailored cover letters in minutes.
        </Typography>
      </Box>

      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        Quick Actions
      </Typography>

      <Grid container spacing={4}>
        {quickActions.map((action, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                  {action.icon}
                </Box>
                <Typography gutterBottom variant="h5" component="h2" align="center">
                  {action.title}
                </Typography>
                <Typography variant="body2" color="textSecondary" align="center">
                  {action.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="large"
                  color="primary"
                  fullWidth
                  onClick={action.action}
                >
                  Get Started
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Home; 