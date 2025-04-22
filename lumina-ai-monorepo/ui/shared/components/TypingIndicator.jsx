import React from 'react';
import PropTypes from 'prop-types';
import { Box, Typography, CircularProgress } from '@mui/material';

/**
 * Typing Indicator Component
 * 
 * Displays an animated indicator when a user is typing
 */
const TypingIndicator = ({ userName }) => {
  return (
    <Box 
      sx={{ 
        display: 'flex', 
        alignItems: 'center',
        p: 1,
        mb: 2
      }}
    >
      <Box 
        sx={{ 
          display: 'flex', 
          alignItems: 'center',
          p: 1,
          borderRadius: 2,
          bgcolor: 'background.paper',
          boxShadow: 1
        }}
      >
        <CircularProgress size={16} thickness={6} sx={{ mr: 1 }} />
        <Typography variant="body2" color="text.secondary">
          {userName ? `${userName} is typing...` : 'Someone is typing...'}
        </Typography>
      </Box>
    </Box>
  );
};

TypingIndicator.propTypes = {
  userName: PropTypes.string
};

export default TypingIndicator;
