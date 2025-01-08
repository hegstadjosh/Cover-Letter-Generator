import React, { useEffect, useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Box,
} from '@mui/material';
import {
  Edit as EditIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { promptsApi, AIPrompt } from '../services/api';

const Settings: React.FC = () => {
  const [prompts, setPrompts] = useState<AIPrompt[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedPrompt, setSelectedPrompt] = useState<AIPrompt | null>(null);
  const [name, setName] = useState('');
  const [content, setContent] = useState('');
  const [description, setDescription] = useState('');

  useEffect(() => {
    loadPrompts();
  }, []);

  const loadPrompts = async () => {
    try {
      const response = await promptsApi.list();
      setPrompts(response.data);
    } catch (error) {
      console.error('Error loading prompts:', error);
    }
  };

  const handleAdd = () => {
    setSelectedPrompt(null);
    setName('');
    setContent('');
    setDescription('');
    setOpenDialog(true);
  };

  const handleEdit = (prompt: AIPrompt) => {
    setSelectedPrompt(prompt);
    setName(prompt.name);
    setContent(prompt.content);
    setDescription(prompt.description || '');
    setOpenDialog(true);
  };

  const handleSubmit = async () => {
    try {
      await promptsApi.save(name, content, description);
      setOpenDialog(false);
      loadPrompts();
    } catch (error) {
      console.error('Error saving prompt:', error);
    }
  };

  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h5">AI Prompts</Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleAdd}
          >
            Add New Prompt
          </Button>
        </Box>

        <List>
          {prompts.map((prompt) => (
            <ListItem key={prompt.name} divider>
              <ListItemText
                primary={prompt.name}
                secondary={prompt.description || 'No description'}
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => handleEdit(prompt)}>
                  <EditIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedPrompt ? 'Edit Prompt' : 'Add New Prompt'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={!!selectedPrompt}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Content"
            fullWidth
            multiline
            rows={10}
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            {selectedPrompt ? 'Save Changes' : 'Add Prompt'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Settings; 