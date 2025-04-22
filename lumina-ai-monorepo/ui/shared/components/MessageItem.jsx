import React from 'react';
import PropTypes from 'prop-types';
import { 
  Box, 
  Typography, 
  Avatar, 
  Paper, 
  Tooltip,
  IconButton,
  Chip
} from '@mui/material';
import { 
  ContentCopy as ContentCopyIcon,
  Code as CodeIcon,
  Download as DownloadIcon,
  Image as ImageIcon,
  InsertDriveFile as FileIcon,
  PictureAsPdf as PdfIcon,
  AudioFile as AudioIcon,
  VideoFile as VideoIcon
} from '@mui/icons-material';
import DOMPurify from 'dompurify';
import { marked } from 'marked';

/**
 * Message Item Component
 * 
 * Displays a single message in the conversation with support for
 * different message types, formats, and attachments.
 */
const MessageItem = ({ message, currentUserId }) => {
  const isCurrentUser = message.sender.id === currentUserId;
  const isAgent = message.sender.type === 'agent';
  
  // Function to get file icon based on file type
  const getFileIcon = (fileType) => {
    if (fileType.startsWith('image/')) return <ImageIcon />;
    if (fileType.startsWith('audio/')) return <AudioIcon />;
    if (fileType.startsWith('video/')) return <VideoIcon />;
    if (fileType === 'application/pdf') return <PdfIcon />;
    return <FileIcon />;
  };
  
  // Function to render message content based on format
  const renderContent = () => {
    if (message.format === 'markdown' || message.format === 'rich') {
      // Sanitize and render markdown/rich content
      const sanitizedContent = DOMPurify.sanitize(marked.parse(message.content));
      return (
        <Box 
          dangerouslySetInnerHTML={{ __html: sanitizedContent }}
          sx={{ 
            '& pre': { 
              backgroundColor: 'rgba(0, 0, 0, 0.04)',
              p: 1,
              borderRadius: 1,
              overflowX: 'auto'
            },
            '& code': {
              backgroundColor: 'rgba(0, 0, 0, 0.04)',
              p: 0.5,
              borderRadius: 0.5,
              fontFamily: 'monospace'
            },
            '& img': {
              maxWidth: '100%',
              borderRadius: 1
            },
            '& a': {
              color: 'primary.main',
              textDecoration: 'none',
              '&:hover': {
                textDecoration: 'underline'
              }
            }
          }}
        />
      );
    }
    
    // Plain text content
    return (
      <Typography variant="body2">
        {message.content}
      </Typography>
    );
  };
  
  // Function to render attachment if present
  const renderAttachment = () => {
    if (!message.attachment) return null;
    
    const { name, type, size, url } = message.attachment;
    const icon = getFileIcon(type);
    
    return (
      <Box 
        sx={{ 
          mt: 1, 
          p: 1.5, 
          bgcolor: 'background.paper', 
          borderRadius: 1,
          border: '1px solid',
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {icon}
          <Box sx={{ ml: 1 }}>
            <Typography variant="body2" fontWeight="medium">
              {name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {(size / 1024).toFixed(1)} KB
            </Typography>
          </Box>
        </Box>
        
        <Tooltip title="Download file">
          <IconButton size="small" component="a" href={url} download={name}>
            <DownloadIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
    );
  };
  
  // Function to render tool execution if present
  const renderToolExecution = () => {
    if (!message.toolExecution) return null;
    
    const { toolId, params } = message.toolExecution;
    
    return (
      <Box 
        sx={{ 
          mt: 1, 
          p: 1.5, 
          bgcolor: 'background.paper', 
          borderRadius: 1,
          border: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
          <CodeIcon fontSize="small" sx={{ mr: 0.5 }} />
          <Typography variant="caption" fontWeight="medium">
            Tool Execution: {toolId}
          </Typography>
        </Box>
        
        <Typography variant="body2" fontFamily="monospace" sx={{ fontSize: '0.8rem', whiteSpace: 'pre-wrap' }}>
          {JSON.stringify(params, null, 2)}
        </Typography>
      </Box>
    );
  };
  
  return (
    <Box 
      sx={{ 
        display: 'flex', 
        mb: 2, 
        justifyContent: isCurrentUser ? 'flex-end' : 'flex-start',
        alignItems: 'flex-start'
      }}
    >
      {!isCurrentUser && (
        <Avatar 
          sx={{ 
            bgcolor: isAgent ? 'primary.main' : 'grey.500', 
            width: 32, 
            height: 32, 
            mr: 1 
          }}
          src={message.sender.avatar}
        >
          {message.sender.name.charAt(0).toUpperCase()}
        </Avatar>
      )}
      
      <Box sx={{ maxWidth: '80%' }}>
        {/* Sender name */}
        <Typography 
          variant="caption" 
          color="text.secondary" 
          sx={{ 
            display: 'block', 
            mb: 0.5, 
            textAlign: isCurrentUser ? 'right' : 'left' 
          }}
        >
          {message.sender.name}
          {isAgent && (
            <Chip 
              label="AI" 
              size="small" 
              color="primary" 
              variant="outlined" 
              sx={{ ml: 1, height: 16, fontSize: '0.6rem' }} 
            />
          )}
        </Typography>
        
        {/* Message content */}
        <Paper 
          sx={{ 
            p: 1.5, 
            bgcolor: isCurrentUser 
              ? 'grey.100' 
              : isAgent 
                ? 'primary.light' 
                : 'background.paper',
            borderTopLeftRadius: !isCurrentUser ? 0 : undefined,
            borderTopRightRadius: isCurrentUser ? 0 : undefined,
            position: 'relative'
          }}
        >
          {renderContent()}
          {renderAttachment()}
          {renderToolExecution()}
          
          {/* Copy button (only visible on hover) */}
          <Tooltip title="Copy message">
            <IconButton 
              size="small" 
              sx={{ 
                position: 'absolute', 
                top: 4, 
                right: 4, 
                opacity: 0,
                transition: 'opacity 0.2s',
                bgcolor: 'background.paper',
                '&:hover': {
                  opacity: 1,
                  bgcolor: 'background.paper',
                }
              }}
              className="message-copy-button"
              onClick={() => navigator.clipboard.writeText(message.content)}
            >
              <ContentCopyIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Paper>
        
        {/* Timestamp */}
        <Typography 
          variant="caption" 
          color="text.secondary" 
          sx={{ 
            display: 'block', 
            mt: 0.5, 
            textAlign: isCurrentUser ? 'right' : 'left' 
          }}
        >
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Typography>
      </Box>
      
      {isCurrentUser && (
        <Avatar 
          sx={{ 
            bgcolor: 'grey.500', 
            width: 32, 
            height: 32, 
            ml: 1 
          }}
          src={message.sender.avatar}
        >
          {message.sender.name.charAt(0).toUpperCase()}
        </Avatar>
      )}
    </Box>
  );
};

MessageItem.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.string.isRequired,
    content: PropTypes.string.isRequired,
    sender: PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      avatar: PropTypes.string,
      type: PropTypes.oneOf(['user', 'agent', 'system'])
    }).isRequired,
    timestamp: PropTypes.string.isRequired,
    format: PropTypes.oneOf(['text', 'markdown', 'rich']),
    attachment: PropTypes.shape({
      name: PropTypes.string.isRequired,
      type: PropTypes.string.isRequired,
      size: PropTypes.number.isRequired,
      url: PropTypes.string.isRequired
    }),
    toolExecution: PropTypes.shape({
      toolId: PropTypes.string.isRequired,
      params: PropTypes.object.isRequired
    })
  }).isRequired,
  currentUserId: PropTypes.string.isRequired
};

export default MessageItem;
