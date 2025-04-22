import React from 'react';
import { Box, Typography, Paper, Tabs, Tab, Button, CircularProgress } from '@mui/material';
import { VisibilityOutlined, CodeOutlined, HistoryOutlined, SettingsOutlined } from '@mui/icons-material';

// Agent Observer Component
const AgentObserver = ({ agentStatus, agentActions, isUserControlling, onTakeControl }) => {
  return (
    <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h2">
          Agent Observer
        </Typography>
        <Button 
          variant="contained" 
          color={isUserControlling ? 'secondary' : 'primary'} 
          onClick={onTakeControl}
        >
          {isUserControlling ? 'Release Control' : 'Take Control'}
        </Button>
      </Box>
      
      <Box sx={{ 
        flex: 1,
        p: 2, 
        border: '1px solid', 
        borderColor: 'divider', 
        borderRadius: 2,
        bgcolor: 'background.default',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {agentStatus === 'working' && !isUserControlling ? (
          <Box sx={{ position: 'absolute', top: 10, right: 10, display: 'flex', alignItems: 'center' }}>
            <CircularProgress size={20} sx={{ mr: 1 }} />
            <Typography variant="body2" color="primary">Agent working...</Typography>
          </Box>
        ) : isUserControlling ? (
          <Box sx={{ position: 'absolute', top: 10, right: 10, display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2" color="secondary">User in control</Typography>
          </Box>
        ) : (
          <Box sx={{ position: 'absolute', top: 10, right: 10, display: 'flex', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">Agent idle</Typography>
          </Box>
        )}
        
        {isUserControlling ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '300px' }}>
            <Typography variant="h3" color="secondary" gutterBottom>
              You are in control
            </Typography>
            <Typography variant="body1" color="text.secondary" align="center">
              You can now interact directly with the workspace.<br />
              The agent will observe and learn from your actions.
            </Typography>
          </Box>
        ) : agentStatus === 'idle' ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '300px' }}>
            <Typography variant="h3" color="text.secondary" gutterBottom>
              Agent is idle
            </Typography>
            <Typography variant="body1" color="text.secondary" align="center">
              Click "Start Agent" to begin working with Lumina AI
            </Typography>
          </Box>
        ) : (
          <Box sx={{ pt: 4 }}>
            <Typography variant="body1">
              The agent is currently working on your task. You can observe its actions in real-time or take control at any point.
            </Typography>
            
            {/* Agent screen visualization */}
            <Box sx={{ mt: 3, border: '1px solid', borderColor: 'divider', borderRadius: 1, overflow: 'hidden' }}>
              {/* Agent screen header */}
              <Box sx={{ p: 1, bgcolor: '#F3F4F6', borderBottom: '1px solid', borderColor: 'divider', display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="caption" fontWeight="medium">Agent Viewport</Typography>
                <Typography variant="caption" color="text.secondary">Real-time view</Typography>
              </Box>
              
              {/* Agent screen content */}
              <Box sx={{ p: 2, minHeight: '200px', bgcolor: '#FFFFFF' }}>
                {agentActions.length > 0 ? (
                  <Box>
                    <Box sx={{ mb: 2, p: 1.5, bgcolor: '#F3F4F6', borderRadius: 1 }}>
                      <Typography variant="body2" fontFamily="monospace">
                        {`> ${agentActions[0]?.description || 'Agent initializing...'}`}
                      </Typography>
                    </Box>
                    
                    {agentActions.length > 1 && (
                      <Box sx={{ p: 1.5, bgcolor: '#F3F4F6', borderRadius: 1 }}>
                        <Typography variant="body2" fontFamily="monospace">
                          {`> ${agentActions[1]?.description || ''}`}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary" align="center" sx={{ pt: 4 }}>
                    Waiting for agent activity...
                  </Typography>
                )}
              </Box>
            </Box>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default AgentObserver;
