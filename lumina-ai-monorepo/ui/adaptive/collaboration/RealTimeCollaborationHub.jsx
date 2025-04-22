import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import PropTypes from 'prop-types';

// Styled components for the collaboration hub
const CollaborationContainer = styled.div`
  position: relative;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  height: 100%;
  transition: all 0.3s ease;
  
  &.active {
    border: 2px solid #007AFF;
  }
  
  @media (prefers-color-scheme: dark) {
    background: #1E1E1E;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  }
`;

const CollaborationHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  
  @media (prefers-color-scheme: dark) {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
`;

const CollaborationTitle = styled.h3`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333333;
  
  @media (prefers-color-scheme: dark) {
    color: #FFFFFF;
  }
`;

const ParticipantsContainer = styled.div`
  display: flex;
  align-items: center;
`;

const ParticipantAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: ${props => props.color || '#007AFF'};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  margin-left: -8px;
  border: 2px solid #FFFFFF;
  position: relative;
  
  &:first-child {
    margin-left: 0;
  }
  
  ${props => props.active && `
    &::after {
      content: '';
      position: absolute;
      bottom: -2px;
      right: -2px;
      width: 10px;
      height: 10px;
      background-color: #34C759;
      border-radius: 50%;
      border: 2px solid #FFFFFF;
    }
  `}
  
  @media (prefers-color-scheme: dark) {
    border: 2px solid #1E1E1E;
    
    ${props => props.active && `
      &::after {
        border: 2px solid #1E1E1E;
      }
    `}
  }
`;

const CollaborationContent = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  position: relative;
  
  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 20px;
  }
  
  @media (prefers-color-scheme: dark) {
    &::-webkit-scrollbar-thumb {
      background-color: rgba(255, 255, 255, 0.2);
    }
  }
`;

const CollaborationFooter = styled.div`
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  
  @media (prefers-color-scheme: dark) {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
`;

const ActionButton = styled.button`
  background: ${props => props.primary ? '#007AFF' : 'transparent'};
  color: ${props => props.primary ? '#FFFFFF' : '#007AFF'};
  border: ${props => props.primary ? 'none' : '1px solid #007AFF'};
  border-radius: 8px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: ${props => props.primary ? '12px' : '0'};
  
  &:hover {
    background: ${props => props.primary ? '#0066CC' : 'rgba(0, 122, 255, 0.1)'};
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  svg {
    margin-right: 8px;
  }
  
  @media (prefers-color-scheme: dark) {
    color: ${props => props.primary ? '#FFFFFF' : '#5AC8FA'};
    border: ${props => props.primary ? 'none' : '1px solid #5AC8FA'};
    
    &:hover {
      background: ${props => props.primary ? '#0066CC' : 'rgba(90, 200, 250, 0.1)'};
    }
  }
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  margin-left: auto;
  margin-right: 16px;
  font-size: 14px;
  color: ${props => {
    switch (props.status) {
      case 'active': return '#34C759';
      case 'paused': return '#FF9500';
      case 'completed': return '#8E8E93';
      default: return '#8E8E93';
    }
  }};
  
  &::before {
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: currentColor;
    margin-right: 6px;
  }
`;

const ActivityOverlay = styled(motion.div)`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.03);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  z-index: 10;
  
  @media (prefers-color-scheme: dark) {
    background: rgba(255, 255, 255, 0.03);
  }
`;

const ActivityIndicator = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  
  @media (prefers-color-scheme: dark) {
    background: rgba(30, 30, 30, 0.9);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  }
`;

const ActivityText = styled.div`
  margin-top: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #333333;
  
  @media (prefers-color-scheme: dark) {
    color: #FFFFFF;
  }
`;

const Spinner = styled.div`
  width: 32px;
  height: 32px;
  border: 3px solid rgba(0, 122, 255, 0.2);
  border-top-color: #007AFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

/**
 * RealTimeCollaborationHub Component
 * 
 * A sophisticated real-time collaboration interface that enables users and AI agents
 * to work together on tasks. Designed to exceed the quality of existing platforms
 * with superior visual design and interaction patterns.
 */
const RealTimeCollaborationHub = ({
  sessionId,
  title,
  participants,
  status = 'active',
  onComplete,
  onCancel,
  children,
  isProcessing = false,
  processingMessage = 'Processing...'
}) => {
  const [isActive, setIsActive] = useState(true);
  const contentRef = useRef(null);
  
  // Auto-scroll to bottom when content changes
  useEffect(() => {
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight;
    }
  }, [children]);
  
  // Get initials for avatar
  const getInitials = (name) => {
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };
  
  // Generate consistent color based on name
  const getAvatarColor = (name) => {
    const colors = [
      '#007AFF', // Blue
      '#FF9500', // Orange
      '#FF2D55', // Pink
      '#5856D6', // Purple
      '#34C759', // Green
      '#AF52DE', // Magenta
      '#FF3B30', // Red
      '#5AC8FA', // Light Blue
    ];
    
    // Simple hash function
    const hash = name.split('').reduce((acc, char) => {
      return acc + char.charCodeAt(0);
    }, 0);
    
    return colors[hash % colors.length];
  };
  
  return (
    <CollaborationContainer className={isActive ? 'active' : ''}>
      <CollaborationHeader>
        <CollaborationTitle>{title}</CollaborationTitle>
        <ParticipantsContainer>
          {participants.map((participant, index) => (
            <ParticipantAvatar
              key={index}
              color={getAvatarColor(participant.name)}
              active={participant.active}
              title={participant.name}
            >
              {getInitials(participant.name)}
            </ParticipantAvatar>
          ))}
        </ParticipantsContainer>
      </CollaborationHeader>
      
      <CollaborationContent ref={contentRef}>
        {children}
        
        <AnimatePresence>
          {isProcessing && (
            <ActivityOverlay
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <ActivityIndicator>
                <Spinner />
                <ActivityText>{processingMessage}</ActivityText>
              </ActivityIndicator>
            </ActivityOverlay>
          )}
        </AnimatePresence>
      </CollaborationContent>
      
      <CollaborationFooter>
        <ActionButton onClick={onCancel}>
          Cancel
        </ActionButton>
        
        <StatusIndicator status={status}>
          {status === 'active' ? 'Collaborating' : 
           status === 'paused' ? 'Paused' : 
           status === 'completed' ? 'Completed' : 'Unknown'}
        </StatusIndicator>
        
        <ActionButton 
          primary 
          onClick={onComplete}
          disabled={status === 'completed' || isProcessing}
        >
          Complete
        </ActionButton>
      </CollaborationFooter>
    </CollaborationContainer>
  );
};

RealTimeCollaborationHub.propTypes = {
  sessionId: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  participants: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string.isRequired,
      active: PropTypes.bool,
      role: PropTypes.string
    })
  ).isRequired,
  status: PropTypes.oneOf(['active', 'paused', 'completed']),
  onComplete: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  children: PropTypes.node,
  isProcessing: PropTypes.bool,
  processingMessage: PropTypes.string
};

export default RealTimeCollaborationHub;
