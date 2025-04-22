import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useDispatch } from 'react-redux';
import { closeNotification, executeNotificationAction } from './notificationSlice';
import '../styles/AdaptiveNotification.css';

/**
 * AdaptiveNotification component for displaying notifications in the Adaptive UI system.
 * Supports different notification types, actions, and auto-dismissal.
 */
const AdaptiveNotification = ({ notification, onAction, onClose }) => {
  const [timeLeft, setTimeLeft] = useState(null);
  const dispatch = useDispatch();
  
  useEffect(() => {
    // Set up countdown timer for chat termination warnings
    if (notification.type === 'warning' && notification.title === 'Chat Session Ending Soon') {
      const match = notification.message.match(/(\d+) seconds/);
      if (match && match[1]) {
        setTimeLeft(parseInt(match[1], 10));
      }
    }
    
    // Set up auto-dismiss timer if duration is specified
    let dismissTimer;
    if (notification.duration > 0) {
      dismissTimer = setTimeout(() => {
        handleClose();
      }, notification.duration);
    }
    
    return () => {
      if (dismissTimer) clearTimeout(dismissTimer);
    };
  }, [notification]);
  
  useEffect(() => {
    // Update countdown timer every second
    if (timeLeft === null) return;
    
    const countdownTimer = setInterval(() => {
      setTimeLeft(prevTime => {
        if (prevTime <= 1) {
          clearInterval(countdownTimer);
          return 0;
        }
        return prevTime - 1;
      });
    }, 1000);
    
    return () => clearInterval(countdownTimer);
  }, [timeLeft]);
  
  const handleAction = () => {
    if (onAction) {
      onAction(notification.id, notification.action);
    } else {
      dispatch(executeNotificationAction({
        id: notification.id,
        action: notification.action,
        sessionId: notification.sessionId
      }));
    }
  };
  
  const handleClose = () => {
    if (onClose) {
      onClose(notification.id);
    } else {
      dispatch(closeNotification(notification.id));
    }
  };
  
  // Determine notification class based on type
  const getNotificationClass = () => {
    switch (notification.type) {
      case 'success': return 'adaptive-notification-success';
      case 'error': return 'adaptive-notification-error';
      case 'warning': return 'adaptive-notification-warning';
      case 'info': return 'adaptive-notification-info';
      default: return 'adaptive-notification-default';
    }
  };
  
  return (
    <div className={`adaptive-notification ${getNotificationClass()}`} role="alert">
      <div className="adaptive-notification-header">
        <h4 className="adaptive-notification-title">{notification.title}</h4>
        {notification.closable && (
          <button 
            className="adaptive-notification-close" 
            onClick={handleClose}
            aria-label="close"
          >
            ×
          </button>
        )}
      </div>
      <div className="adaptive-notification-body">
        <p className="adaptive-notification-message">
          {timeLeft !== null 
            ? notification.message.replace(/\d+ seconds/, `${timeLeft} seconds`) 
            : notification.message
          }
        </p>
        {notification.action && notification.actionText && (
          <button 
            className="adaptive-notification-action" 
            onClick={handleAction}
          >
            {notification.actionText}
          </button>
        )}
      </div>
    </div>
  );
};

AdaptiveNotification.propTypes = {
  notification: PropTypes.shape({
    id: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    message: PropTypes.string.isRequired,
    closable: PropTypes.bool,
    action: PropTypes.string,
    actionText: PropTypes.string,
    duration: PropTypes.number,
    sessionId: PropTypes.string
  }).isRequired,
  onAction: PropTypes.func,
  onClose: PropTypes.func
};

export default AdaptiveNotification;
