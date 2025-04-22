import { createSlice } from '@reduxjs/toolkit';

/**
 * Redux slice for managing notifications across the application.
 * Handles creation, display, and dismissal of notifications.
 */
const notificationSlice = createSlice({
  name: 'notifications',
  initialState: {
    notifications: [],
    nextId: 1
  },
  reducers: {
    // Add a new notification
    addNotification: (state, action) => {
      const { type = 'default', title, message, duration = 5000, closable = true, action: actionName, actionText } = action.payload;
      
      const id = `notification-${state.nextId}`;
      state.nextId += 1;
      
      state.notifications.push({
        id,
        type,
        title,
        message,
        duration,
        closable,
        action: actionName,
        actionText,
        createdAt: new Date().toISOString()
      });
    },
    
    // Remove a notification by ID
    removeNotification: (state, action) => {
      const id = action.payload;
      state.notifications = state.notifications.filter(notification => notification.id !== id);
    },
    
    // Clear all notifications
    clearNotifications: (state) => {
      state.notifications = [];
    }
  }
});

export const {
  addNotification,
  removeNotification,
  clearNotifications
} = notificationSlice.actions;

// Selectors
export const selectNotifications = state => state.notifications.notifications;

// Thunks
export const showNotification = (notification) => (dispatch) => {
  dispatch(addNotification(notification));
  
  // Auto-dismiss after duration if specified
  if (notification.duration && notification.duration > 0) {
    setTimeout(() => {
      dispatch(removeNotification(`notification-${notification.id}`));
    }, notification.duration);
  }
};

export const showSuccessNotification = (title, message, options = {}) => (dispatch) => {
  dispatch(showNotification({
    type: 'success',
    title,
    message,
    ...options
  }));
};

export const showErrorNotification = (title, message, options = {}) => (dispatch) => {
  dispatch(showNotification({
    type: 'error',
    title,
    message,
    ...options
  }));
};

export const showWarningNotification = (title, message, options = {}) => (dispatch) => {
  dispatch(showNotification({
    type: 'warning',
    title,
    message,
    ...options
  }));
};

export const showInfoNotification = (title, message, options = {}) => (dispatch) => {
  dispatch(showNotification({
    type: 'info',
    title,
    message,
    ...options
  }));
};

export const showChatTerminationWarning = (timeRemaining, sessionId, options = {}) => (dispatch) => {
  dispatch(showNotification({
    type: 'warning',
    title: 'Chat Session Ending Soon',
    message: `This chat session will terminate in ${timeRemaining} seconds.`,
    duration: 0, // Don't auto-dismiss
    action: 'extendSession',
    actionText: 'Extend Session',
    sessionId,
    ...options
  }));
  
  // Dispatch custom event for bridge component
  const event = new CustomEvent('chat-termination-warning', { 
    detail: { timeRemaining, sessionId } 
  });
  window.dispatchEvent(event);
};

export default notificationSlice.reducer;
