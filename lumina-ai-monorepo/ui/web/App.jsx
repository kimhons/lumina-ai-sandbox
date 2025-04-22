import React, { useState, useEffect } from 'react';
import { Box, Container, Grid, Typography, Paper, Button, CircularProgress, Tabs, Tab } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { VisibilityOutlined, CodeOutlined, HistoryOutlined, SettingsOutlined, SwapHorizOutlined } from '@mui/icons-material';

// Create a theme instance with a modern, minimalistic design
const theme = createTheme({
  palette: {
    primary: {
      main: '#6366F1', // Indigo
    },
    secondary: {
      main: '#10B981', // Emerald
    },
    background: {
      default: '#F9FAFB',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#111827',
      secondary: '#6B7280',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0px 1px 2px rgba(0, 0, 0, 0.05)',
    '0px 1px 3px rgba(0, 0, 0, 0.1), 0px 1px 2px rgba(0, 0, 0, 0.06)',
    // ... other shadow levels
    '0px 20px 25px -5px rgba(0, 0, 0, 0.1), 0px 10px 10px -5px rgba(0, 0, 0, 0.04)',
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '10px 16px',
        },
        containedPrimary: {
          boxShadow: '0px 1px 3px rgba(0, 0, 0, 0.1), 0px 1px 2px rgba(0, 0, 0, 0.06)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0px 1px 3px rgba(0, 0, 0, 0.1), 0px 1px 2px rgba(0, 0, 0, 0.06)',
        },
      },
    },
  },
});

// Main application component
const App = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [agentStatus, setAgentStatus] = useState('idle');
  const [agentActions, setAgentActions] = useState([]);
  const [isUserControlling, setIsUserControlling] = useState(false);

  // Simulate agent activity for demonstration
  useEffect(() => {
    const interval = setInterval(() => {
      if (agentStatus === 'working' && !isUserControlling) {
        const newAction = {
          id: Date.now(),
          type: ['search', 'read', 'analyze', 'write'][Math.floor(Math.random() * 4)],
          description: `Agent is ${['searching for information', 'reading content', 'analyzing data', 'writing response'][Math.floor(Math.random() * 4)]}`,
          timestamp: new Date().toISOString(),
        };
        setAgentActions(prev => [newAction, ...prev].slice(0, 10));
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [agentStatus, isUserControlling]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const toggleAgentStatus = () => {
    setAgentStatus(prev => prev === 'idle' ? 'working' : 'idle');
  };

  const toggleUserControl = () => {
    setIsUserControlling(prev => !prev);
  };

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', pb: 4 }}>
        <Container maxWidth="xl">
          {/* Header */}
          <Box sx={{ py: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h1" component="h1" sx={{ color: 'primary.main' }}>
              Lumina AI
            </Typography>
            <Box>
              <Button 
                variant="outlined" 
                color="primary" 
                onClick={toggleAgentStatus}
                sx={{ mr: 2 }}
              >
                {agentStatus === 'idle' ? 'Start Agent' : 'Pause Agent'}
              </Button>
              <Button 
                variant="contained" 
                color={isUserControlling ? 'secondary' : 'primary'} 
                onClick={toggleUserControl}
                startIcon={<SwapHorizOutlined />}
              >
                {isUserControlling ? 'Release Control' : 'Take Control'}
              </Button>
            </Box>
          </Box>

          {/* Main content */}
          <Grid container spacing={3}>
            {/* Left sidebar - Navigation */}
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Tabs
                  orientation="vertical"
                  value={activeTab}
                  onChange={handleTabChange}
                  sx={{ borderRight: 1, borderColor: 'divider' }}
                >
                  <Tab icon={<VisibilityOutlined />} label="Observer" />
                  <Tab icon={<CodeOutlined />} label="Workspace" />
                  <Tab icon={<HistoryOutlined />} label="History" />
                  <Tab icon={<SettingsOutlined />} label="Settings" />
                </Tabs>
              </Paper>
            </Grid>

            {/* Main content area */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3, minHeight: '70vh' }}>
                {activeTab === 0 && (
                  <Box>
                    <Typography variant="h2" gutterBottom>
                      Agent Observer
                    </Typography>
                    <Box sx={{ 
                      p: 2, 
                      border: '1px solid', 
                      borderColor: 'divider', 
                      borderRadius: 2,
                      bgcolor: 'background.default',
                      minHeight: '50vh',
                      position: 'relative'
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
                          {/* This would be replaced with actual agent screen/actions */}
                          <Box sx={{ mt: 2, p: 2, bgcolor: '#F3F4F6', borderRadius: 1 }}>
                            <Typography variant="body2" fontFamily="monospace">
                              {`> ${agentActions[0]?.description || 'Agent initializing...'}`}
                            </Typography>
                          </Box>
                        </Box>
                      )}
                    </Box>
                  </Box>
                )}

                {activeTab === 1 && (
                  <Box>
                    <Typography variant="h2" gutterBottom>
                      Collaborative Workspace
                    </Typography>
                    <Typography variant="body1" paragraph>
                      This is where you and the agent can work together on tasks.
                    </Typography>
                    {/* Workspace content would go here */}
                  </Box>
                )}

                {activeTab === 2 && (
                  <Box>
                    <Typography variant="h2" gutterBottom>
                      Session History
                    </Typography>
                    <Typography variant="body1" paragraph>
                      Review past interactions and results.
                    </Typography>
                    {/* History content would go here */}
                  </Box>
                )}

                {activeTab === 3 && (
                  <Box>
                    <Typography variant="h2" gutterBottom>
                      Settings
                    </Typography>
                    <Typography variant="body1" paragraph>
                      Configure your Lumina AI experience.
                    </Typography>
                    {/* Settings content would go here */}
                  </Box>
                )}
              </Paper>
            </Grid>

            {/* Right sidebar - Agent activity */}
            <Grid item xs={12} md={3}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h3" gutterBottom>
                  Agent Activity
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
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default App;
