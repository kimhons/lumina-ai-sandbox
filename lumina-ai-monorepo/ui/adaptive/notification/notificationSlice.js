import { createSlice } from '@reduxjs/toolkit';

/**
 * Redux slice for managing notifications in the Adaptive UI system.
 */
const notificationSlice = createSlice({
  name: 'notifications',
  initialState: {
    items: [],
    nextId: 1
  },
  reducers: {
    addNotification: (state, action) => {
      const id = `notification-${state.nextId}`;
      state.items.push({
        ...action.payload,
        id,
        createdAt: new Date().toISOString(),
        read: false
      });
      state.nextId += 1;
    },
    closeNotification: (state, action) => {
      state.items = state.items.filter(item => item.id !== action.payload);
    },
    markAsRead: (state, action) => {
      const notification = state.items.find(item => item.id === action.payload);
      if (notification) {
        notification.read = true;
      }
    },
    clearAllNotifications: (state) => {
      state.items = [];
    },
    executeNotificationAction: (state, action) => {
      // This is handled by the middleware, no state change needed here
    },
    showChatTerminationWarning: (state, action) => {
      // This is handled by the middleware, which will dispatch addNotification
    }
  }
});

export const { 
  addNotification, 
  closeNotification, 
  markAsRead, 
  clearAllNotifications,
  executeNotificationAction,
  showChatTerminationWarning
} = notificationSlice.actions;

export default notificationSlice.reducer;

// Middleware to handle notification actions
export const notificationMiddleware = store => next => action => {
  if (action.type === showChatTerminationWarning.type) {
    const { timeRemaining, sessionId } = action.payload;
    store.dispatch(addNotification({
      type: 'warning',
      title: 'Chat Session Ending Soon',
      message: `This chat session will terminate in ${timeRemaining} seconds.`,
      action: 'extendSession',
      actionText: 'Extend Session',
      closable: true,
      duration: 0,
      sessionId
    }));
  }
  
  if (action.type === executeNotificationAction.type) {
    const { id, action: actionType, sessionId } = action.payload;
    
    // Handle different action types
    if (actionType === 'extendSession' && sessionId) {
      // In a real implementation, this would call an API to extend the session
      console.log(`Extending session ${sessionId}`);
      
      // Close the notification
      store.dispatch(closeNotification(id));
      
      // Show a success notification
      store.dispatch(addNotification({
        type: 'success',
        title: 'Session Extended',
        message: 'Your chat session has been extended.',
        closable: true,
        duration: 3000
      }));
    }
  }
  
  return next(action);
};
