import React, { useState, ChangeEvent } from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Paper,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { documentsApi } from '../services/api';

interface Document {
  name: string;
  created_at: string;
  content?: string;
  company?: string;
  position?: string;
}

interface DocumentListProps {
  title: string;
  documents: Document[];
  documentType: 'cover_letter' | 'resume' | 'job_description';
  onAdd: (name: string, content: string) => void;
  onDelete: (name: string) => void;
  onEdit?: (name: string, content: string) => void;
  showCompanyInfo?: boolean;
}

const DocumentList = ({
  title,
  documents,
  documentType,
  onAdd,
  onDelete,
  onEdit,
  showCompanyInfo = false,
}: DocumentListProps) => {
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState<'add' | 'edit'>('add');
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [name, setName] = useState('');
  const [content, setContent] = useState('');

  const handleAdd = () => {
    setDialogMode('add');
    setName('');
    setContent('');
    setOpenDialog(true);
  };

  const handleEdit = async (doc: Document) => {
    setDialogMode('edit');
    setSelectedDoc(doc);
    setName(doc.name);
    try {
      const response = await documentsApi.get(documentType, doc.name);
      setContent(response.data.content);
    } catch (error) {
      console.error('Error fetching document content:', error);
      setContent('');
    }
    setOpenDialog(true);
  };

  const handleSubmit = () => {
    if (dialogMode === 'add') {
      onAdd(name, content);
    } else if (dialogMode === 'edit' && onEdit) {
      onEdit(selectedDoc?.name || '', content);
    }
    setOpenDialog(false);
  };

  return (
    <>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Button
          startIcon={<AddIcon />}
          variant="contained"
          color="primary"
          onClick={handleAdd}
          sx={{ mb: 2 }}
        >
          Add New
        </Button>
        <List>
          {documents.map((doc) => (
            <ListItem key={doc.name} divider>
              <ListItemText
                primary={doc.name}
                secondary={
                  showCompanyInfo && doc.company
                    ? `${doc.company} - ${doc.position}`
                    : doc.created_at
                }
              />
              <ListItemSecondaryAction>
                {onEdit && (
                  <IconButton edge="end" onClick={() => handleEdit(doc)} sx={{ mr: 1 }}>
                    <EditIcon />
                  </IconButton>
                )}
                <IconButton edge="end" onClick={() => onDelete(doc.name)}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{dialogMode === 'add' ? 'Add New' : 'Edit'} {title}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={name}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
            disabled={dialogMode === 'edit'}
          />
          <TextField
            margin="dense"
            label="Content"
            fullWidth
            multiline
            rows={10}
            value={content}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setContent(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            {dialogMode === 'add' ? 'Add' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default DocumentList; 