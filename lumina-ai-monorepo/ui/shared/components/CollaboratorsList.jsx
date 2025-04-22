import React from 'react';
import PropTypes from 'prop-types';
import { 
  Box, 
  Typography, 
  Avatar, 
  AvatarGroup, 
  Tooltip,
  Badge
} from '@mui/material';

/**
 * Collaborators List Component
 * 
 * Displays a list of active collaborators in the workspace
 * with their online status and activity indicators.
 */
const CollaboratorsList = ({ collaborators }) => {
  if (!collaborators || collaborators.length === 0) {
    return null;
  }
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
      <AvatarGroup max={4} sx={{ '& .MuiAvatar-root': { width: 32, height: 32, fontSize: '0.875rem' } }}>
        {collaborators.map((collaborator) => (
          <Tooltip 
            key={collaborator.id} 
            title={`${collaborator.name} (${collaborator.status === 'active' ? 'Active' : 'Idle'})`}
          >
            <Badge
              overlap="circular"
              anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
              variant="dot"
              color={collaborator.status === 'active' ? 'success' : 'default'}
            >
              <Avatar 
                alt={collaborator.name} 
                src={collaborator.avatar}
                sx={{ 
                  bgcolor: collaborator.type === 'agent' ? 'primary.main' : 'grey.500',
                }}
              >
                {collaborator.name.charAt(0).toUpperCase()}
              </Avatar>
            </Badge>
          </Tooltip>
        ))}
      </AvatarGroup>
      
      <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
        {collaborators.length} {collaborators.length === 1 ? 'collaborator' : 'collaborators'}
      </Typography>
    </Box>
  );
};

CollaboratorsList.propTypes = {
  collaborators: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      avatar: PropTypes.string,
      status: PropTypes.oneOf(['active', 'idle']).isRequired,
      type: PropTypes.oneOf(['user', 'agent']).isRequired
    })
  ).isRequired
};

export default CollaboratorsList;
