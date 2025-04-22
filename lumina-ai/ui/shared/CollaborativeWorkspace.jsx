import React from 'react';
import { Box, Typography, Paper, TextField, Button, Divider, Avatar } from '@mui/material';
import { Send as SendIcon, Code as CodeIcon } from '@mui/icons-material';

// Collaborative Workspace Component
const CollaborativeWorkspace = ({ isUserControlling, agentStatus, onSendMessage }) => {
  const [message, setMessage] = React.useState('');
  
  const handleSendMessage = () => {
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  return (
    <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h2" gutterBottom>
        Collaborative Workspace
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        {isUserControlling 
          ? "You're in control. The agent is observing your actions."
          : agentStatus === 'working'
            ? "The agent is working on your task. You can collaborate or take control at any time."
            : "Start the agent or take control to begin working on tasks."}
      </Typography>
      
      <Divider sx={{ my: 2 }} />
      
      {/* Conversation/Collaboration Area */}
      <Box sx={{ 
        flex: 1, 
        mb: 2, 
        p: 2, 
        bgcolor: 'background.default', 
        borderRadius: 2,
        overflow: 'auto',
        border: '1px solid',
        borderColor: 'divider'
      }}>
        {/* Example conversation */}
        <Box sx={{ display: 'flex', mb: 2 }}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32, mr: 1 }}>L</Avatar>
          <Paper sx={{ p: 1.5, maxWidth: '80%', bgcolor: 'primary.light', borderTopLeftRadius: 0 }}>
            <Typography variant="body2">
              I'm analyzing the data you provided. The key insights appear to be related to user engagement patterns.
            </Typography>
          </Paper>
        </Box>
        
        <Box sx={{ display: 'flex', mb: 2, justifyContent: 'flex-end' }}>
          <Paper sx={{ p: 1.5, maxWidth: '80%', bgcolor: 'grey.100', borderTopRightRadius: 0 }}>
            <Typography variant="body2">
              Can you create a visualization of the weekly engagement trends?
            </Typography>
          </Paper>
          <Avatar sx={{ bgcolor: 'grey.500', width: 32, height: 32, ml: 1 }}>U</Avatar>
        </Box>
        
        <Box sx={{ display: 'flex', mb: 2 }}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32, mr: 1 }}>L</Avatar>
          <Paper sx={{ p: 1.5, maxWidth: '80%', bgcolor: 'primary.light', borderTopLeftRadius: 0 }}>
            <Typography variant="body2">
              Creating a visualization of weekly engagement trends. Here's what I found:
            </Typography>
            <Box sx={{ 
              mt: 1, 
              p: 1, 
              bgcolor: 'background.paper', 
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'divider'
            }}>
              <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                <CodeIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                Visualization
              </Typography>
              <Typography variant="body2" fontFamily="monospace" sx={{ fontSize: '0.8rem' }}>
                [Weekly engagement visualization would appear here]
              </Typography>
            </Box>
          </Paper>
        </Box>
      </Box>
      
      {/* Input Area */}
      <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder="Type a message or command..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          variant="outlined"
          sx={{ mr: 1 }}
        />
        <Button 
          variant="contained" 
          color="primary"
          endIcon={<SendIcon />}
          onClick={handleSendMessage}
          disabled={!message.trim()}
        >
          Send
        </Button>
      </Box>
    </Paper>
  );
};

export default CollaborativeWorkspace;
