import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import AdaptiveNotification from './AdaptiveNotification';
import { closeNotification, executeNotificationAction } from './notificationSlice';
import '../styles/NotificationProvider.css';

/**
 * NotificationProvider component for managing and displaying notifications in the Adaptive UI system.
 * Renders all active notifications from the Redux store.
 */
const NotificationProvider = () => {
  const notifications = useSelector(state => state.notifications.items);
  const dispatch = useDispatch();
  
  const handleAction = (id, action) => {
    dispatch(executeNotificationAction({ id, action }));
  };
  
  const handleClose = (id) => {
    dispatch(closeNotification(id));
  };
  
  if (!notifications || notifications.length === 0) {
    return null;
  }
  
  return (
    <div className="adaptive-notification-container" aria-live="polite">
      {notifications.map(notification => (
        <AdaptiveNotification
          key={notification.id}
          notification={notification}
          onAction={handleAction}
          onClose={handleClose}
        />
      ))}
    </div>
  );
};

export default NotificationProvider;
