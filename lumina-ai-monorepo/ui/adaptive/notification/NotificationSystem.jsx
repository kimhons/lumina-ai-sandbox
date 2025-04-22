import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import styled, { keyframes } from 'styled-components';

// Animation for notification appearance
const slideIn = keyframes`
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
`;

// Animation for notification disappearance
const slideOut = keyframes`
  from {
    transform: translateY(0);
    opacity: 1;
  }
  to {
    transform: translateY(-100%);
    opacity: 0;
  }
`;

// Styled components for the notification system
const NotificationContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  pointer-events: none;
`;

const NotificationItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 600px;
  margin-bottom: 10px;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background-color: ${props => {
    switch (props.priority) {
      case 'critical':
        return '#FF3B30';
      case 'high':
        return '#FF9500';
      case 'medium':
        return '#34C759';
      default:
        return '#007AFF';
    }
  }};
  color: white;
  animation: ${props => (props.exiting ? slideOut : slideIn)} 0.3s ease-in-out;
  pointer-events: auto;
  opacity: ${props => (props.exiting ? 0 : 1)};
`;

const NotificationContent = styled.div`
  flex: 1;
`;

const NotificationTitle = styled.h4`
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
`;

const NotificationMessage = styled.p`
  margin: 0;
  font-size: 14px;
`;

const NotificationActions = styled.div`
  display: flex;
  margin-left: 20px;
`;

const NotificationButton = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 4px;
  color: white;
  padding: 6px 12px;
  margin-left: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }
`;

const CloseButton = styled.button`
  background: transparent;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  margin-left: 10px;
  opacity: 0.7;
  transition: opacity 0.2s;

  &:hover {
    opacity: 1;
  }
`;

/**
 * NotificationSystem Component
 * 
 * A comprehensive notification system that supports different priority levels,
 * actions, and automatic dismissal. Specially designed to handle critical
 * notifications like chat termination warnings.
 */
const NotificationSystem = ({ maxNotifications = 3 }) => {
  const [notifications, setNotifications] = useState([]);
  const [exitingIds, setExitingIds] = useState(new Set());

  // Function to add a new notification
  const addNotification = useCallback((notification) => {
    const id = notification.id || Date.now().toString();
    const newNotification = {
      ...notification,
      id,
      created: new Date(),
      read: false,
      dismissed: false,
    };

    setNotifications(prev => {
      // Sort notifications by priority (critical first)
      const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      
      return [...prev, newNotification].sort((a, b) => 
        priorityOrder[a.priority] - priorityOrder[b.priority]
      ).slice(-maxNotifications);
    });

    // Auto-dismiss non-critical notifications
    if (notification.priority !== 'critical' && notification.autoDismiss !== false) {
      const dismissTime = notification.dismissTime || 5000;
      setTimeout(() => {
        dismissNotification(id);
      }, dismissTime);
    }

    return id;
  }, [maxNotifications]);

  // Function to dismiss a notification
  const dismissNotification = useCallback((id) => {
    setExitingIds(prev => new Set(prev).add(id));
    
    // Remove notification after animation completes
    setTimeout(() => {
      setExitingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(id);
        return newSet;
      });
      
      setNotifications(prev => 
        prev.filter(notification => notification.id !== id)
      );
    }, 300); // Match animation duration
  }, []);

  // Function to handle notification action
  const handleAction = useCallback((id, action) => {
    if (action.onClick) {
      action.onClick();
    }
    
    if (action.dismissOnClick) {
      dismissNotification(id);
    }
  }, [dismissNotification]);

  // Expose the notification API via window for global access
  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.NotificationSystem = {
        addNotification,
        dismissNotification,
        
        // Special function for chat termination warning
        showChatTerminationWarning: (timeRemaining, onExtend) => {
          return addNotification({
            priority: 'critical',
            title: 'Chat Session Ending Soon',
            message: `Your chat session will terminate in ${timeRemaining} seconds.`,
            autoDismiss: false,
            actions: [
              {
                label: 'Extend Session',
                onClick: onExtend,
                dismissOnClick: true
              }
            ]
          });
        }
      };
    }
    
    return () => {
      if (typeof window !== 'undefined') {
        delete window.NotificationSystem;
      }
    };
  }, [addNotification, dismissNotification]);

  return (
    <NotificationContainer>
      {notifications.map(notification => (
        <NotificationItem 
          key={notification.id}
          priority={notification.priority}
          exiting={exitingIds.has(notification.id)}
        >
          <NotificationContent>
            <NotificationTitle>{notification.title}</NotificationTitle>
            <NotificationMessage>{notification.message}</NotificationMessage>
          </NotificationContent>
          
          {notification.actions && notification.actions.length > 0 && (
            <NotificationActions>
              {notification.actions.map((action, index) => (
                <NotificationButton
                  key={index}
                  onClick={() => handleAction(notification.id, action)}
                >
                  {action.label}
                </NotificationButton>
              ))}
            </NotificationActions>
          )}
          
          <CloseButton onClick={() => dismissNotification(notification.id)}>
            ×
          </CloseButton>
        </NotificationItem>
      ))}
    </NotificationContainer>
  );
};

NotificationSystem.propTypes = {
  maxNotifications: PropTypes.number
};

export default NotificationSystem;
