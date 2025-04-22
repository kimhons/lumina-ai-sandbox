import React, { useState, useEffect } from 'react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import chatReducer from './chat/chatSlice';
import preferencesReducer from './preferences/preferencesSlice';
import notificationReducer from './common/notificationSlice';
import AdaptiveUIRoot from './layout/AdaptiveUIRoot';
import AdaptiveUIBridge from './layout/AdaptiveUIBridge';
import NotificationProvider from './common/NotificationProvider';

/**
 * Create Redux store with all reducers for the Adaptive UI system
 */
const createStore = () => {
  return configureStore({
    reducer: {
      chat: chatReducer,
      preferences: preferencesReducer,
      notifications: notificationReducer
    }
  });
};

/**
 * Main entry point for the Adaptive UI system
 * This file exports all necessary components for integration with both repositories
 */

// Export the main components
export { default as AdaptiveLayout } from './layout/AdaptiveLayout';
export { default as AdaptiveUIIntegration } from './layout/AdaptiveUIIntegration';
export { default as AdaptiveUIRoot } from './layout/AdaptiveUIRoot';
export { default as AdaptiveUIBridge } from './layout/AdaptiveUIBridge';

// Export chat components
export { default as AdaptiveChatInterface } from './chat/AdaptiveChatInterface';
export { default as ChatProvider } from './chat/ChatProvider';

// Export preferences components
export { default as AdaptivePreferencesPanel } from './preferences/AdaptivePreferencesPanel';
export { default as PreferencesProvider } from './preferences/PreferencesProvider';

// Export collaboration components
export { default as CollaborationWorkspace } from './collaboration/CollaborationWorkspace';
export { default as CaptchaBypassCollaboration } from './collaboration/CaptchaBypassCollaboration';

// Export common components
export { default as AdaptiveModal } from './common/AdaptiveModal';
export { default as AdaptiveNotification } from './common/AdaptiveNotification';
export { default as NotificationProvider } from './common/NotificationProvider';

// Export Redux slices and actions
export { 
  createChatSession, 
  setActiveChatSession,
  addMessage,
  updateMessageStatus,
  setTypingStatus,
  updateSessionTimeout,
  extendSessionTimeout,
  endChatSession,
  updatePreferences,
  toggleTheme,
  clearChatHistory
} from './chat/chatSlice';

export {
  updatePreferenceCategory,
  updatePreference,
  setTheme,
  resetPreferences,
  importPreferences,
  savePreferencesToStorage,
  loadPreferencesFromStorage
} from './preferences/preferencesSlice';

export {
  addNotification,
  removeNotification,
  clearNotifications,
  showNotification,
  showSuccessNotification,
  showErrorNotification,
  showWarningNotification,
  showInfoNotification,
  showChatTerminationWarning
} from './common/notificationSlice';

/**
 * AdaptiveUI Component
 * 
 * The main component that wraps the entire application with the Adaptive UI system.
 * This component can be used in different modes:
 * - standalone: Replace the existing UI completely
 * - overlay: Overlay the adaptive UI on top of the existing UI
 * - hybrid: Use both UIs together, switching between them as needed
 */
const AdaptiveUI = ({
  children,
  userId,
  userName,
  initialView = 'chat',
  mode = 'hybrid'
}) => {
  const [store] = useState(createStore);
  
  return (
    <Provider store={store}>
      {mode === 'standalone' ? (
        <>
          <AdaptiveUIRoot
            userId={userId}
            userName={userName}
            initialView={initialView}
          />
          <NotificationProvider position="bottom" />
        </>
      ) : (
        <>
          <AdaptiveUIBridge
            adaptiveUI={
              <AdaptiveUIRoot
                userId={userId}
                userName={userName}
                initialView={initialView}
              />
            }
            adaptiveMode={mode}
          >
            {children}
          </AdaptiveUIBridge>
          <NotificationProvider position="bottom" />
        </>
      )}
    </Provider>
  );
};

export default AdaptiveUI;
