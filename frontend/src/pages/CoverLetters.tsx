import React, { useEffect, useState } from 'react';
import { Container } from '@mui/material';
import DocumentList from '../components/DocumentList';
import { documentsApi, Document } from '../services/api';

const CoverLetters: React.FC = () => {
  const [coverLetters, setCoverLetters] = useState<Document[]>([]);

  useEffect(() => {
    loadCoverLetters();
  }, []);

  const loadCoverLetters = async () => {
    try {
      const response = await documentsApi.list('cover_letter');
      setCoverLetters(response.data);
    } catch (error) {
      console.error('Error loading cover letters:', error);
    }
  };

  const handleAdd = async (name: string, content: string) => {
    try {
      await documentsApi.create('cover_letter', { name, content });
      loadCoverLetters();
    } catch (error) {
      console.error('Error adding cover letter:', error);
    }
  };

  const handleDelete = async (name: string) => {
    try {
      await documentsApi.delete('cover_letter', name);
      loadCoverLetters();
    } catch (error) {
      console.error('Error deleting cover letter:', error);
    }
  };

  const handleEdit = async (name: string, content: string) => {
    try {
      await documentsApi.create('cover_letter', { name, content });
      loadCoverLetters();
    } catch (error) {
      console.error('Error updating cover letter:', error);
    }
  };

  return (
    <Container maxWidth="lg">
      <DocumentList
        title="Cover Letters"
        documents={coverLetters}
        documentType="cover_letter"
        onAdd={handleAdd}
        onDelete={handleDelete}
        onEdit={handleEdit}
      />
    </Container>
  );
};

export default CoverLetters; 