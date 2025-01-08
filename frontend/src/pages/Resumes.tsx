import React, { useEffect, useState } from 'react';
import { Container } from '@mui/material';
import DocumentList from '../components/DocumentList';
import { documentsApi, Document } from '../services/api';

const Resumes: React.FC = () => {
  const [resumes, setResumes] = useState<Document[]>([]);

  useEffect(() => {
    loadResumes();
  }, []);

  const loadResumes = async () => {
    try {
      const response = await documentsApi.list('resume');
      setResumes(response.data);
    } catch (error) {
      console.error('Error loading resumes:', error);
    }
  };

  const handleAdd = async (name: string, content: string) => {
    try {
      await documentsApi.create('resume', { name, content });
      loadResumes();
    } catch (error) {
      console.error('Error adding resume:', error);
    }
  };

  const handleDelete = async (name: string) => {
    try {
      await documentsApi.delete('resume', name);
      loadResumes();
    } catch (error) {
      console.error('Error deleting resume:', error);
    }
  };

  const handleEdit = async (name: string, content: string) => {
    try {
      await documentsApi.create('resume', { name, content });
      loadResumes();
    } catch (error) {
      console.error('Error updating resume:', error);
    }
  };

  return (
    <Container maxWidth="lg">
      <DocumentList
        title="Resumes"
        documents={resumes}
        documentType="resume"
        onAdd={handleAdd}
        onDelete={handleDelete}
        onEdit={handleEdit}
      />
    </Container>
  );
};

export default Resumes; 