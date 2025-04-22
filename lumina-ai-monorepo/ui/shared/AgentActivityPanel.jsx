import React from 'react';
import { Box, Typography, Paper, Button, CircularProgress } from '@mui/material';
import { VisibilityOutlined, SwapHorizOutlined } from '@mui/icons-material';

// Agent Activity Panel Component
const AgentActivityPanel = ({ agentStatus, agentActions, isUserControlling }) => {
  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <VisibilityOutlined sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h3">
          Agent Activity
        </Typography>
      </Box>
      
      {/* Status indicator */}
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        p: 1.5, 
        mb: 2, 
        borderRadius: 1, 
        bgcolor: isUserControlling ? 'secondary.light' : agentStatus === 'working' ? 'primary.light' : 'grey.100'
      }}>
        {agentStatus === 'working' && !isUserControlling && <CircularProgress size={16} sx={{ mr: 1 }} />}
        <Typography variant="body2" fontWeight="medium">
          {isUserControlling 
            ? 'User is in control' 
            : agentStatus === 'working' 
              ? 'Agent is actively working' 
              : 'Agent is idle'}
        </Typography>
      </Box>
      
      {/* Activity feed */}
      <Typography variant="subtitle2" sx={{ mb: 1 }}>
        Recent Actions:
      </Typography>
      <Box sx={{ maxHeight: '60vh', overflow: 'auto' }}>
        {agentActions.length > 0 ? (
          agentActions.map(action => (
            <Box 
              key={action.id} 
              sx={{ 
                p: 1.5, 
                mb: 1, 
                borderRadius: 1, 
                bgcolor: 'background.default',
                border: '1px solid',
                borderColor: 'divider'
              }}
            >
              <Typography variant="body2" fontWeight="medium">
                {action.description}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {new Date(action.timestamp).toLocaleTimeString()}
              </Typography>
            </Box>
          ))
        ) : (
          <Typography variant="body2" color="text.secondary">
            No recent activity
          </Typography>
        )}
      </Box>
      
      {/* Control button */}
      <Box sx={{ mt: 2 }}>
        <Button 
          variant="contained" 
          color={isUserControlling ? 'secondary' : 'primary'} 
          fullWidth
          startIcon={<SwapHorizOutlined />}
        >
          {isUserControlling ? 'Release Control' : 'Take Control'}
        </Button>
      </Box>
    </Paper>
  );
};

export default AgentActivityPanel;
