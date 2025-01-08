import React, { useEffect, useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Save as SaveIcon,
  History as HistoryIcon,
  Restore as RestoreIcon,
} from '@mui/icons-material';
import { biographyApi, Biography } from '../services/api';

const BiographyPage: React.FC = () => {
  const [currentBio, setCurrentBio] = useState<Biography | null>(null);
  const [content, setContent] = useState('');
  const [notes, setNotes] = useState('');
  const [versions, setVersions] = useState<Biography[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    loadBiography();
    loadVersions();
  }, []);

  const loadBiography = async () => {
    try {
      const response = await biographyApi.get();
      setCurrentBio(response.data);
      setContent(response.data.content);
    } catch (error) {
      console.error('Error loading biography:', error);
    }
  };

  const loadVersions = async () => {
    try {
      const response = await biographyApi.getVersions();
      setVersions(response.data);
    } catch (error) {
      console.error('Error loading versions:', error);
    }
  };

  const handleSave = async () => {
    try {
      await biographyApi.update(content, notes);
      setNotes('');
      loadBiography();
      loadVersions();
    } catch (error) {
      console.error('Error saving biography:', error);
    }
  };

  const handleRestore = async (version: number) => {
    try {
      const response = await biographyApi.getVersion(version);
      const oldVersion = response.data;
      await biographyApi.update(
        oldVersion.content,
        `Reverted to version ${version}`
      );
      setShowHistory(false);
      loadBiography();
      loadVersions();
    } catch (error) {
      console.error('Error restoring version:', error);
    }
  };

  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Professional Biography
        </Typography>
        <TextField
          fullWidth
          multiline
          rows={10}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Enter your professional biography..."
          variant="outlined"
          sx={{ mb: 2 }}
        />
        <TextField
          fullWidth
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Notes about this update (optional)"
          variant="outlined"
          sx={{ mb: 2 }}
        />
        <Button
          variant="contained"
          color="primary"
          startIcon={<SaveIcon />}
          onClick={handleSave}
        >
          Save Changes
        </Button>
        <Button
          variant="outlined"
          startIcon={<HistoryIcon />}
          onClick={() => setShowHistory(true)}
          sx={{ ml: 2 }}
        >
          View History
        </Button>
      </Paper>

      <Dialog
        open={showHistory}
        onClose={() => setShowHistory(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Version History</DialogTitle>
        <DialogContent>
          <List>
            {versions.map((version) => (
              <ListItem key={version.version} divider>
                <ListItemText
                  primary={`Version ${version.version}`}
                  secondary={`${version.created_at}${
                    version.notes ? ` - ${version.notes}` : ''
                  }`}
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    onClick={() => handleRestore(version.version)}
                  >
                    <RestoreIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHistory(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default BiographyPage; 