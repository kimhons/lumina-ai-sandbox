import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  TextField, 
  Button, 
  Divider, 
  Avatar, 
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
  CircularProgress,
  Chip,
  Tabs,
  Tab,
  Drawer,
  Snackbar,
  Alert
} from '@mui/material';
import { 
  Send as SendIcon, 
  Code as CodeIcon, 
  MoreVert as MoreVertIcon,
  ContentCopy as ContentCopyIcon,
  Save as SaveIcon,
  Share as ShareIcon,
  PersonAdd as PersonAddIcon,
  Attachment as AttachmentIcon,
  Image as ImageIcon,
  InsertDriveFile as FileIcon,
  FormatBold as FormatBoldIcon,
  FormatItalic as FormatItalicIcon,
  FormatListBulleted as FormatListBulletedIcon,
  FormatListNumbered as FormatListNumberedIcon,
  Code as CodeBlockIcon,
  Link as LinkIcon
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { v4 as uuidv4 } from 'uuid';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { Socket } from 'socket.io-client';

// Import sub-components
import MessageItem from './components/MessageItem';
import CollaboratorsList from './components/CollaboratorsList';
import TypingIndicator from './components/TypingIndicator';
import FileUploader from './components/FileUploader';
import ToolSelector from './components/ToolSelector';
import RichTextEditor from './components/RichTextEditor';

/**
 * Enhanced Collaborative Workspace Component
 * 
 * This component provides a real-time collaborative environment where users and AI agents
 * can work together on tasks, share context, and utilize tools.
 */
const EnhancedCollaborativeWorkspace = ({ 
  isUserControlling, 
  agentStatus, 
  onSendMessage,
  onToggleControl,
  onSelectTool,
  onShareWorkspace,
  onSaveSession,
  socket, // Socket.io connection for real-time collaboration
  availableTools = [],
  collaborators = [],
  userId,
  userName,
  userAvatar
}) => {
  const theme = useTheme();
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [typingUser, setTypingUser] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [showToolDrawer, setShowToolDrawer] = useState(false);
  const [selectedTool, setSelectedTool] = useState(null);
  const [toolResults, setToolResults] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const [anchorEl, setAnchorEl] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [useRichEditor, setUseRichEditor] = useState(false);
  const [richText, setRichText] = useState('');
  
  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Socket event listeners for real-time collaboration
  useEffect(() => {
    if (socket) {
      // Listen for new messages
      socket.on('new_message', (data) => {
        setMessages(prev => [...prev, data]);
      });
      
      // Listen for typing indicators
      socket.on('user_typing', (data) => {
        if (data.userId !== userId) {
          setIsTyping(true);
          setTypingUser(data.userName);
          
          // Clear typing indicator after 3 seconds
          setTimeout(() => {
            setIsTyping(false);
            setTypingUser(null);
          }, 3000);
        }
      });
      
      // Listen for tool results
      socket.on('tool_result', (data) => {
        setToolResults(data);
        setNotification({
          open: true,
          message: `Tool "${data.toolName}" execution completed`,
          severity: data.success ? 'success' : 'error'
        });
      });
      
      // Listen for collaborator updates
      socket.on('collaborator_joined', (data) => {
        setNotification({
          open: true,
          message: `${data.userName} joined the workspace`,
          severity: 'info'
        });
      });
      
      socket.on('collaborator_left', (data) => {
        setNotification({
          open: true,
          message: `${data.userName} left the workspace`,
          severity: 'info'
        });
      });
      
      // Clean up listeners on unmount
      return () => {
        socket.off('new_message');
        socket.off('user_typing');
        socket.off('tool_result');
        socket.off('collaborator_joined');
        socket.off('collaborator_left');
      };
    }
  }, [socket, userId]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const handleSendMessage = () => {
    if ((message.trim() || richText.trim()) && !isUploading) {
      const newMessage = {
        id: uuidv4(),
        content: useRichEditor ? richText : message,
        sender: {
          id: userId,
          name: userName,
          avatar: userAvatar,
          type: 'user'
        },
        timestamp: new Date().toISOString(),
        format: useRichEditor ? 'rich' : 'text'
      };
      
      // Add message to local state
      setMessages(prev => [...prev, newMessage]);
      
      // Send message to server/agent
      onSendMessage(useRichEditor ? richText : message);
      
      // Emit message to other collaborators if socket exists
      if (socket) {
        socket.emit('send_message', newMessage);
      }
      
      // Clear input
      setMessage('');
      setRichText('');
    }
  };
  
  const handleKeyPress = (e) => {
    if (!useRichEditor && e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
    
    // Emit typing event
    if (socket && (message.trim() || richText.trim())) {
      socket.emit('typing', {
        userId,
        userName
      });
    }
  };
  
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleCopyConversation = () => {
    const conversationText = messages
      .map(msg => `${msg.sender.name} (${new Date(msg.timestamp).toLocaleTimeString()}): ${msg.content}`)
      .join('\n\n');
    
    navigator.clipboard.writeText(conversationText);
    
    setNotification({
      open: true,
      message: 'Conversation copied to clipboard',
      severity: 'success'
    });
    
    handleMenuClose();
  };
  
  const handleSaveSession = () => {
    onSaveSession(messages);
    
    setNotification({
      open: true,
      message: 'Session saved successfully',
      severity: 'success'
    });
    
    handleMenuClose();
  };
  
  const handleShareWorkspace = () => {
    onShareWorkspace();
    handleMenuClose();
  };
  
  const handleFileUpload = (files) => {
    setIsUploading(true);
    
    // Simulate file upload
    setTimeout(() => {
      const fileMessages = Array.from(files).map(file => ({
        id: uuidv4(),
        content: `Uploaded file: ${file.name}`,
        sender: {
          id: userId,
          name: userName,
          avatar: userAvatar,
          type: 'user'
        },
        timestamp: new Date().toISOString(),
        attachment: {
          name: file.name,
          type: file.type,
          size: file.size,
          url: URL.createObjectURL(file)
        }
      }));
      
      setMessages(prev => [...prev, ...fileMessages]);
      
      // Emit file messages to other collaborators if socket exists
      if (socket) {
        fileMessages.forEach(msg => {
          socket.emit('send_message', msg);
        });
      }
      
      setIsUploading(false);
      
      setNotification({
        open: true,
        message: `${files.length} file(s) uploaded successfully`,
        severity: 'success'
      });
    }, 1500);
  };
  
  const handleToolSelect = (tool) => {
    setSelectedTool(tool);
    setShowToolDrawer(true);
    
    if (onSelectTool) {
      onSelectTool(tool);
    }
  };
  
  const handleToolExecute = (toolId, params) => {
    // Simulate tool execution
    setNotification({
      open: true,
      message: `Executing tool "${toolId}"...`,
      severity: 'info'
    });
    
    // Close tool drawer
    setShowToolDrawer(false);
    
    // Add tool execution message
    const toolMessage = {
      id: uuidv4(),
      content: `Executing tool: ${toolId} with parameters: ${JSON.stringify(params)}`,
      sender: {
        id: userId,
        name: userName,
        avatar: userAvatar,
        type: 'user'
      },
      timestamp: new Date().toISOString(),
      toolExecution: {
        toolId,
        params
      }
    };
    
    setMessages(prev => [...prev, toolMessage]);
    
    // Emit tool execution to other collaborators if socket exists
    if (socket) {
      socket.emit('send_message', toolMessage);
      socket.emit('execute_tool', { toolId, params });
    }
  };
  
  const handleCloseNotification = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    
    setNotification({ ...notification, open: false });
  };
  
  const toggleEditorMode = () => {
    setUseRichEditor(!useRichEditor);
  };
  
  return (
    <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h2" gutterBottom>
          Collaborative Workspace
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <CollaboratorsList collaborators={collaborators} />
          
          <Tooltip title="Workspace options">
            <IconButton onClick={handleMenuOpen}>
              <MoreVertIcon />
            </IconButton>
          </Tooltip>
          
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleCopyConversation}>
              <ContentCopyIcon fontSize="small" sx={{ mr: 1 }} />
              Copy conversation
            </MenuItem>
            <MenuItem onClick={handleSaveSession}>
              <SaveIcon fontSize="small" sx={{ mr: 1 }} />
              Save session
            </MenuItem>
            <MenuItem onClick={handleShareWorkspace}>
              <ShareIcon fontSize="small" sx={{ mr: 1 }} />
              Share workspace
            </MenuItem>
            <Divider />
            <MenuItem onClick={toggleEditorMode}>
              <CodeIcon fontSize="small" sx={{ mr: 1 }} />
              {useRichEditor ? 'Switch to plain text' : 'Switch to rich editor'}
            </MenuItem>
          </Menu>
        </Box>
      </Box>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        {isUserControlling 
          ? "You're in control. The agent is observing your actions."
          : agentStatus === 'working'
            ? "The agent is working on your task. You can collaborate or take control at any time."
            : "Start the agent or take control to begin working on tasks."}
      </Typography>
      
      {/* Tabs */}
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
        <Tab label="Conversation" />
        <Tab label="Context" />
        <Tab label="Tools" />
      </Tabs>
      
      {/* Main content area */}
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
        {activeTab === 0 && (
          /* Conversation tab */
          <Box>
            {messages.map((msg) => (
              <MessageItem 
                key={msg.id} 
                message={msg} 
                currentUserId={userId} 
              />
            ))}
            
            {isTyping && (
              <TypingIndicator userName={typingUser} />
            )}
            
            <div ref={messagesEndRef} />
          </Box>
        )}
        
        {activeTab === 1 && (
          /* Context tab */
          <Box>
            <Typography variant="h6" gutterBottom>
              Shared Context
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              This tab shows the current context shared between you and the agent.
            </Typography>
            
            {/* Context items would be displayed here */}
            <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
              <Typography variant="subtitle2">
                Current Task
              </Typography>
              <Typography variant="body2">
                Implementing enhanced UI components for Lumina AI, focusing on the Collaborative Workspace.
              </Typography>
            </Paper>
            
            <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
              <Typography variant="subtitle2">
                Relevant Files
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                <Chip icon={<FileIcon />} label="CollaborativeWorkspace.jsx" size="small" />
                <Chip icon={<FileIcon />} label="App.jsx" size="small" />
                <Chip icon={<FileIcon />} label="AgentActivityPanel.jsx" size="small" />
              </Box>
            </Paper>
            
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Typography variant="subtitle2">
                Memory References
              </Typography>
              <Typography variant="body2">
                Connected to 3 memory clusters related to UI development, React components, and collaboration features.
              </Typography>
            </Paper>
          </Box>
        )}
        
        {activeTab === 2 && (
          /* Tools tab */
          <Box>
            <Typography variant="h6" gutterBottom>
              Available Tools
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Select a tool to use in your workflow.
            </Typography>
            
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              {availableTools.map((tool) => (
                <Paper 
                  key={tool.id}
                  variant="outlined" 
                  sx={{ 
                    p: 2, 
                    width: 200, 
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    '&:hover': {
                      boxShadow: 3,
                      borderColor: 'primary.main'
                    }
                  }}
                  onClick={() => handleToolSelect(tool)}
                >
                  <Typography variant="subtitle2">
                    {tool.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {tool.description}
                  </Typography>
                </Paper>
              ))}
              
              {availableTools.length === 0 && (
                <Typography variant="body2" color="text.secondary">
                  No tools available. The agent will use its built-in capabilities.
                </Typography>
              )}
            </Box>
          </Box>
        )}
      </Box>
      
      {/* Input Area */}
      <Box sx={{ display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', mb: 1 }}>
          <Tooltip title="Attach files">
            <IconButton 
              color="primary" 
              onClick={() => fileInputRef.current.click()}
              disabled={isUploading}
            >
              <AttachmentIcon />
            </IconButton>
          </Tooltip>
          
          <FileUploader 
            ref={fileInputRef}
            onUpload={handleFileUpload}
            multiple
          />
          
          <Box sx={{ flex: 1 }} />
          
          {useRichEditor && (
            <Box sx={{ display: 'flex' }}>
              <Tooltip title="Bold">
                <IconButton size="small">
                  <FormatBoldIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Italic">
                <IconButton size="small">
                  <FormatItalicIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Bullet List">
                <IconButton size="small">
                  <FormatListBulletedIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Numbered List">
                <IconButton size="small">
                  <FormatListNumberedIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Code Block">
                <IconButton size="small">
                  <CodeBlockIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Link">
                <IconButton size="small">
                  <LinkIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          )}
          
          <Tooltip title={useRichEditor ? "Switch to plain text" : "Switch to rich editor"}>
            <IconButton color="primary" onClick={toggleEditorMode}>
              <CodeIcon />
            </IconButton>
          </Tooltip>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
          {useRichEditor ? (
            <RichTextEditor
              value={richText}
              onChange={setRichText}
              onSubmit={handleSendMessage}
              placeholder="Type a message or command..."
              sx={{ flex: 1, mr: 1 }}
            />
          ) : (
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
              disabled={isUploading}
            />
          )}
          
          <Button 
            variant="contained" 
            color="primary"
            endIcon={isUploading ? <CircularProgress size={20} /> : <SendIcon />}
            onClick={handleSendMessage}
            disabled={(!message.trim() && !richText.trim()) || isUploading}
          >
            Send
          </Button>
        </Box>
      </Box>
      
      {/* Tool Drawer */}
      <Drawer
        anchor="right"
        open={showToolDrawer}
        onClose={() => setShowToolDrawer(false)}
        sx={{
          '& .MuiDrawer-paper': {
            width: '400px',
            p: 3
          }
        }}
      >
        {selectedTool && (
          <Box>
            <Typography variant="h6" gutterBottom>
              {selectedTool.name}
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              {selectedTool.description}
            </Typography>
            
            <Divider sx={{ my: 2 }} />
            
            <ToolSelector
              tool={selectedTool}
              onExecute={handleToolExecute}
              onCancel={() => setShowToolDrawer(false)}
            />
          </Box>
        )}
      </Drawer>
      
      {/* Notifications */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseNotification} 
          severity={notification.severity} 
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

export default EnhancedCollaborativeWorkspace;
