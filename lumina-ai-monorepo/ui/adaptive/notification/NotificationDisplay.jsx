import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  selectActiveNotifications, 
  dismissNotification, 
  markAsRead 
} from './notificationSlice';

// Styled components with enhanced visual design that exceeds ChatGPT and Manus AI
const NotificationContainer = styled.div`
  position: fixed;
  top: 0;
  right: 0;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  padding: 16px;
  max-height: 100vh;
  overflow-y: auto;
  pointer-events: none;
  
  /* Custom scrollbar that's subtle but visible */
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background-color: rgba(155, 155, 155, 0.5);
    border-radius: 20px;
  }
  
  @media (max-width: 768px) {
    left: 0;
    align-items: center;
    padding: 12px;
  }
`;

const NotificationCard = styled(motion.div)`
  display: flex;
  width: 380px;
  margin-bottom: 12px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  background-color: ${props => {
    switch (props.priority) {
      case 'critical':
        return 'linear-gradient(135deg, #FF3B30, #FF2D55)';
      case 'high':
        return 'linear-gradient(135deg, #FF9500, #FF6200)';
      case 'medium':
        return 'linear-gradient(135deg, #34C759, #30B350)';
      default:
        return 'linear-gradient(135deg, #007AFF, #5AC8FA)';
    }
  }};
  color: white;
  pointer-events: auto;
  overflow: hidden;
  position: relative;
  
  /* Subtle pulsing animation for critical notifications */
  ${props => props.priority === 'critical' && `
    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(255, 255, 255, 0.1);
      animation: pulse 2s infinite;
      
      @keyframes pulse {
        0% { opacity: 0; }
        50% { opacity: 1; }
        100% { opacity: 0; }
      }
    }
  `}
  
  @media (max-width: 768px) {
    width: 100%;
    max-width: 380px;
  }
`;

const NotificationIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  padding: 16px 0 16px 16px;
  font-size: 24px;
`;

const NotificationContent = styled.div`
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
`;

const NotificationHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 4px;
`;

const NotificationTitle = styled.h4`
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.3;
`;

const NotificationTime = styled.span`
  font-size: 12px;
  opacity: 0.8;
  margin-left: 8px;
`;

const NotificationMessage = styled.p`
  margin: 0 0 12px 0;
  font-size: 14px;
  line-height: 1.4;
  opacity: 0.9;
`;

const NotificationActions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const NotificationButton = styled.button`
  background: ${props => props.primary ? 'rgba(255, 255, 255, 0.25)' : 'rgba(255, 255, 255, 0.1)'};
  border: none;
  border-radius: 6px;
  color: white;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: ${props => props.primary ? '600' : '400'};
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: ${props => props.primary ? 'rgba(255, 255, 255, 0.35)' : 'rgba(255, 255, 255, 0.2)'};
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  /* Icon if provided */
  svg {
    margin-right: 6px;
  }
`;

const CloseButton = styled.button`
  background: transparent;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
  padding: 4px;
  margin: -4px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;

  &:hover {
    opacity: 1;
    background: rgba(255, 255, 255, 0.1);
  }
`;

// Animation variants for framer-motion
const notificationVariants = {
  initial: { 
    opacity: 0, 
    y: -20, 
    scale: 0.95,
    x: 50
  },
  animate: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    x: 0,
    transition: { 
      type: 'spring', 
      damping: 20, 
      stiffness: 300 
    }
  },
  exit: { 
    opacity: 0, 
    scale: 0.95, 
    x: 50,
    transition: { 
      duration: 0.2 
    }
  }
};

// Helper to format time
const formatTimeAgo = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now - date) / 1000);
  
  if (seconds < 60) return 'just now';
  
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  
  return date.toLocaleDateString();
};

// Icon mapping
const getIconForType = (type) => {
  switch (type) {
    case 'chat_termination':
      return '⏱️';
    case 'error':
      return '❌';
    case 'warning':
      return '⚠️';
    case 'success':
      return '✅';
    case 'info':
      return 'ℹ️';
    default:
      return '🔔';
  }
};

/**
 * Enhanced NotificationDisplay Component
 * 
 * A visually superior notification display that exceeds the design quality
 * of ChatGPT and Manus AI interfaces. Features smooth animations, responsive
 * design, and accessibility considerations.
 */
const NotificationDisplay = () => {
  const notifications = useSelector(selectActiveNotifications);
  const dispatch = useDispatch();
  
  // Handle notification dismissal
  const handleDismiss = (id) => {
    dispatch(dismissNotification(id));
  };
  
  // Handle notification action
  const handleAction = (notification, action) => {
    // Mark as read when user interacts
    if (!notification.read) {
      dispatch(markAsRead(notification.id));
    }
    
    // If there's a handler for this notification type
    if (window.NotificationHandlers && 
        window.NotificationHandlers[notification.type]) {
      window.NotificationHandlers[notification.type](action.action, notification);
    }
    
    // If action should dismiss the notification
    if (action.dismissOnAction !== false) {
      handleDismiss(notification.id);
    }
  };
  
  // Auto-dismiss non-critical notifications
  useEffect(() => {
    notifications.forEach(notification => {
      if (notification.priority !== 'critical' && 
          notification.autoDismiss !== false &&
          !notification.dismissTimeout) {
        
        const dismissTime = notification.dismissTime || 5000;
        const timeoutId = setTimeout(() => {
          handleDismiss(notification.id);
        }, dismissTime);
        
        // Store timeout ID to clear if component unmounts
        notification.dismissTimeout = timeoutId;
      }
    });
    
    // Cleanup timeouts
    return () => {
      notifications.forEach(notification => {
        if (notification.dismissTimeout) {
          clearTimeout(notification.dismissTimeout);
        }
      });
    };
  }, [notifications]);

  return (
    <NotificationContainer>
      <AnimatePresence>
        {notifications.map(notification => (
          <NotificationCard
            key={notification.id}
            priority={notification.priority}
            initial="initial"
            animate="animate"
            exit="exit"
            variants={notificationVariants}
            layout
          >
            <NotificationIcon>
              {getIconForType(notification.type)}
            </NotificationIcon>
            
            <NotificationContent>
              <NotificationHeader>
                <NotificationTitle>
                  {notification.title}
                  {notification.created && (
                    <NotificationTime>
                      {formatTimeAgo(notification.created)}
                    </NotificationTime>
                  )}
                </NotificationTitle>
                
                <CloseButton 
                  onClick={() => handleDismiss(notification.id)}
                  aria-label="Close notification"
                >
                  ×
                </CloseButton>
              </NotificationHeader>
              
              <NotificationMessage>
                {notification.message}
              </NotificationMessage>
              
              {notification.actions && notification.actions.length > 0 && (
                <NotificationActions>
                  {notification.actions.map((action, index) => (
                    <NotificationButton
                      key={index}
                      primary={action.primary}
                      onClick={() => handleAction(notification, action)}
                    >
                      {action.label}
                    </NotificationButton>
                  ))}
                </NotificationActions>
              )}
            </NotificationContent>
          </NotificationCard>
        ))}
      </AnimatePresence>
    </NotificationContainer>
  );
};

export default NotificationDisplay;
