import React, { useEffect, useState } from 'react';
import { Container } from '@mui/material';
import DocumentList from '../components/DocumentList';
import { documentsApi, Document } from '../services/api';

const JobDescriptions: React.FC = () => {
  const [jobDescriptions, setJobDescriptions] = useState<Document[]>([]);

  useEffect(() => {
    loadJobDescriptions();
  }, []);

  const loadJobDescriptions = async () => {
    try {
      const response = await documentsApi.list('job_description');
      setJobDescriptions(response.data);
    } catch (error) {
      console.error('Error loading job descriptions:', error);
    }
  };

  const handleAdd = async (name: string, content: string) => {
    try {
      // Extract company and position from name (format: "Company - Position")
      const [company, position] = name.split(' - ');
      const metadata = { company, position };
      
      await documentsApi.create('job_description', { name, content, metadata });
      loadJobDescriptions();
    } catch (error) {
      console.error('Error adding job description:', error);
    }
  };

  const handleDelete = async (name: string) => {
    try {
      await documentsApi.delete('job_description', name);
      loadJobDescriptions();
    } catch (error) {
      console.error('Error deleting job description:', error);
    }
  };

  const handleEdit = async (name: string, content: string) => {
    try {
      // Extract company and position from name (format: "Company - Position")
      const [company, position] = name.split(' - ');
      const metadata = { company, position };
      
      await documentsApi.create('job_description', { name, content, metadata });
      loadJobDescriptions();
    } catch (error) {
      console.error('Error updating job description:', error);
    }
  };

  return (
    <Container maxWidth="lg">
      <DocumentList
        title="Job Descriptions"
        documents={jobDescriptions}
        documentType="job_description"
        onAdd={handleAdd}
        onDelete={handleDelete}
        onEdit={handleEdit}
        showCompanyInfo
      />
    </Container>
  );
};

export default JobDescriptions; 