import React, { useContext, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { initializeSession, selectActiveSession } from './chatSlice';
import { showChatTerminationWarning } from '../notification/notificationSlice';
import '../styles/ChatProvider.css';

/**
 * Context for providing chat functionality throughout the application
 */
export const ChatContext = React.createContext({
  activeSession: null,
  sendMessage: () => {},
  startNewSession: () => {},
  endSession: () => {}
});

/**
 * ChatProvider component for managing chat sessions and providing chat functionality
 * to child components through context.
 */
const ChatProvider = ({ children, userId, userName }) => {
  const dispatch = useDispatch();
  const activeSession = useSelector(selectActiveSession);
  
  useEffect(() => {
    // Initialize a chat session when the provider mounts
    if (userId && userName) {
      dispatch(initializeSession(userId, userName));
    }
  }, [userId, userName, dispatch]);
  
  useEffect(() => {
    // Set up session timeout warning
    if (activeSession?.expiresAt) {
      const expiresAt = new Date(activeSession.expiresAt).getTime();
      const warningTime = 30000; // 30 seconds before expiration
      
      const timeUntilWarning = expiresAt - Date.now() - warningTime;
      
      let warningTimer;
      if (timeUntilWarning > 0) {
        warningTimer = setTimeout(() => {
          dispatch(showChatTerminationWarning({
            timeRemaining: 30,
            sessionId: activeSession.id
          }));
        }, timeUntilWarning);
      }
      
      return () => {
        if (warningTimer) clearTimeout(warningTimer);
      };
    }
  }, [activeSession, dispatch]);
  
  const sendMessage = (content) => {
    if (!activeSession) return;
    
    dispatch({
      type: 'chat/sendMessage',
      payload: {
        sessionId: activeSession.id,
        content
      }
    });
  };
  
  const startNewSession = () => {
    dispatch(initializeSession(userId, userName));
  };
  
  const endSession = () => {
    if (!activeSession) return;
    
    dispatch({
      type: 'chat/closeSession',
      payload: activeSession.id
    });
  };
  
  const contextValue = {
    activeSession,
    sendMessage,
    startNewSession,
    endSession
  };
  
  return (
    <ChatContext.Provider value={contextValue}>
      {children}
    </ChatContext.Provider>
  );
};

/**
 * Hook for using chat functionality in components
 */
export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

export default ChatProvider;
