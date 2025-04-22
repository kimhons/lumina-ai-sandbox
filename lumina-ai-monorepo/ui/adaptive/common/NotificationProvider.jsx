import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import PropTypes from 'prop-types';
import { selectNotifications, removeNotification } from './notificationSlice';
import AdaptiveNotification from './AdaptiveNotification';

/**
 * NotificationProvider Component
 * 
 * A wrapper component that connects the AdaptiveNotification component to Redux state
 * and provides notification management functionality.
 */
const NotificationProvider = ({
  position = 'bottom',
  width = '350px',
  animation = 'auto'
}) => {
  const dispatch = useDispatch();
  const notifications = useSelector(selectNotifications);
  
  // Handle notification close
  const handleClose = (id) => {
    dispatch(removeNotification(id));
  };
  
  // Handle notification action
  const handleAction = (id, action) => {
    // Find the notification
    const notification = notifications.find(n => n.id === id);
    
    if (!notification) return;
    
    // Handle different actions
    switch (action) {
      case 'extendSession':
        if (notification.sessionId) {
          // Dispatch action to extend session
          // This would typically be handled by the chat slice
          const event = new CustomEvent('extend-session', { 
            detail: { sessionId: notification.sessionId } 
          });
          window.dispatchEvent(event);
        }
        break;
        
      default:
        // For custom actions, dispatch a generic event
        const event = new CustomEvent('notification-action', { 
          detail: { id, action, notification } 
        });
        window.dispatchEvent(event);
        break;
    }
    
    // Close the notification after action is taken
    handleClose(id);
  };
  
  // Don't render if no notifications
  if (notifications.length === 0) {
    return null;
  }
  
  return (
    <AdaptiveNotification
      notifications={notifications}
      position={position}
      width={width}
      animation={animation}
      onClose={handleClose}
      onAction={handleAction}
    />
  );
};

NotificationProvider.propTypes = {
  position: PropTypes.oneOf(['top', 'bottom', 'left', 'right']),
  width: PropTypes.string,
  animation: PropTypes.oneOf(['slideIn', 'slideUp', 'fadeIn', 'auto'])
};

export default NotificationProvider;
