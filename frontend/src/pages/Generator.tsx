import React, { useEffect, useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Alert,
} from '@mui/material';
import { documentsApi, generatorApi, Document } from '../services/api';

const steps = ['Select Documents', 'Add Preferences', 'Generate Letter'];

const Generator: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [resumes, setResumes] = useState<Document[]>([]);
  const [coverLetters, setCoverLetters] = useState<Document[]>([]);
  const [jobDescriptions, setJobDescriptions] = useState<Document[]>([]);
  const [selectedResume, setSelectedResume] = useState('');
  const [selectedSampleLetter, setSelectedSampleLetter] = useState('');
  const [selectedJobDescription, setSelectedJobDescription] = useState('');
  const [preferences, setPreferences] = useState('');
  const [generatedLetter, setGeneratedLetter] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const [resumesRes, lettersRes, jobsRes] = await Promise.all([
        documentsApi.list('resume'),
        documentsApi.list('cover_letter'),
        documentsApi.list('job_description'),
      ]);
      setResumes(resumesRes.data);
      setCoverLetters(lettersRes.data);
      setJobDescriptions(jobsRes.data);
    } catch (error) {
      console.error('Error loading documents:', error);
      setError('Failed to load documents');
    }
  };

  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      handleGenerate();
    } else {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    try {
      console.log('Generation Request:', {
        resume_name: selectedResume,
        job_description_name: selectedJobDescription,
        sample_letter_name: selectedSampleLetter,
        preferences,
      });

      const response = await generatorApi.generate({
        resume_name: selectedResume,
        job_description_name: selectedJobDescription,
        sample_letter_name: selectedSampleLetter,
        preferences,
      });

      console.log('Generation Response:', response.data);
      
      if (!response.data.cover_letter) {
        throw new Error('No cover letter in response');
      }

      setGeneratedLetter(response.data.cover_letter);
      console.log('Generated Letter Length:', response.data.cover_letter.length);
      
      // Log the analysis data too
      if (response.data.user_profile) console.log('User Profile:', response.data.user_profile);
      if (response.data.job_analysis) console.log('Job Analysis:', response.data.job_analysis);
      if (response.data.alignment) console.log('Profile-Job Alignment:', response.data.alignment);

      // Don't increment step since we're already on the last step
    } catch (error: any) {
      console.error('Detailed generation error:', {
        error,
        message: error.message,
        response: error.response?.data,
      });
      setError(error.response?.data?.error || error.message || 'Failed to generate cover letter');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!generatedLetter) return;

    try {
      const jobDesc = jobDescriptions.find(
        (job) => job.name === selectedJobDescription
      );
      const name = `${jobDesc?.company || 'Company'} - Cover Letter`;
      await documentsApi.create('cover_letter', {
        name,
        content: generatedLetter,
      });
      setActiveStep(0);
      setGeneratedLetter('');
      setPreferences('');
    } catch (error) {
      console.error('Error saving cover letter:', error);
      setError('Failed to save cover letter');
    }
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Resume</InputLabel>
              <Select
                value={selectedResume}
                onChange={(e) => setSelectedResume(e.target.value)}
                label="Resume"
              >
                {resumes.map((resume) => (
                  <MenuItem key={resume.name} value={resume.name}>
                    {resume.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Sample Cover Letter</InputLabel>
              <Select
                value={selectedSampleLetter}
                onChange={(e) => setSelectedSampleLetter(e.target.value)}
                label="Sample Cover Letter"
              >
                {coverLetters.map((letter) => (
                  <MenuItem key={letter.name} value={letter.name}>
                    {letter.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Job Description</InputLabel>
              <Select
                value={selectedJobDescription}
                onChange={(e) => setSelectedJobDescription(e.target.value)}
                label="Job Description"
              >
                {jobDescriptions.map((job) => (
                  <MenuItem key={job.name} value={job.name}>
                    {job.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        );
      case 1:
        return (
          <TextField
            fullWidth
            multiline
            rows={4}
            value={preferences}
            onChange={(e) => setPreferences(e.target.value)}
            label="Additional Preferences"
            placeholder="Enter any specific preferences for tone, style, or content..."
          />
        );
      case 2:
        return loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box>
            <TextField
              fullWidth
              multiline
              rows={12}
              value={generatedLetter}
              onChange={(e) => setGeneratedLetter(e.target.value)}
              variant="outlined"
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleSave}
              sx={{ mt: 2 }}
            >
              Save Cover Letter
            </Button>
          </Box>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Generate Cover Letter
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {getStepContent(activeStep)}

        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
            sx={{ mr: 1 }}
          >
            Back
          </Button>
          <Button
            variant="contained"
            onClick={activeStep === steps.length - 1 ? handleGenerate : handleNext}
            disabled={
              activeStep === 0 &&
              (!selectedResume ||
                !selectedSampleLetter ||
                !selectedJobDescription)
            }
          >
            {activeStep === steps.length - 1 ? 'Generate' : 'Next'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Generator; 