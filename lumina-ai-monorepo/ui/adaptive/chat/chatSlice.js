import { createSlice } from '@reduxjs/toolkit';

/**
 * Redux slice for managing chat functionality in the Adaptive UI system.
 */
const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    sessions: {},
    activeSessionId: null,
    isLoading: false,
    error: null
  },
  reducers: {
    createSession: (state, action) => {
      const { id, userId, userName, expiresAt } = action.payload;
      state.sessions[id] = {
        id,
        userId,
        userName,
        expiresAt,
        messages: [],
        createdAt: new Date().toISOString(),
        isActive: true
      };
      state.activeSessionId = id;
    },
    setActiveSession: (state, action) => {
      state.activeSessionId = action.payload;
    },
    addMessage: (state, action) => {
      const { sessionId, message } = action.payload;
      if (state.sessions[sessionId]) {
        state.sessions[sessionId].messages.push(message);
      }
    },
    setTypingStatus: (state, action) => {
      const { sessionId, isTyping } = action.payload;
      if (state.sessions[sessionId]) {
        state.sessions[sessionId].isTyping = isTyping;
      }
    },
    extendSession: (state, action) => {
      const { sessionId, newExpiryTime } = action.payload;
      if (state.sessions[sessionId]) {
        state.sessions[sessionId].expiresAt = newExpiryTime;
      }
    },
    closeSession: (state, action) => {
      const sessionId = action.payload;
      if (state.sessions[sessionId]) {
        state.sessions[sessionId].isActive = false;
      }
      if (state.activeSessionId === sessionId) {
        // Find another active session to set as active
        const activeSessionIds = Object.keys(state.sessions).filter(
          id => state.sessions[id].isActive
        );
        state.activeSessionId = activeSessionIds.length > 0 ? activeSessionIds[0] : null;
      }
    },
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
      state.isLoading = false;
    }
  }
});

export const {
  createSession,
  setActiveSession,
  addMessage,
  setTypingStatus,
  extendSession,
  closeSession,
  setLoading,
  setError
} = chatSlice.actions;

export default chatSlice.reducer;

// Selectors
export const selectActiveSession = state => {
  const activeSessionId = state.chat.activeSessionId;
  return activeSessionId ? state.chat.sessions[activeSessionId] : null;
};

export const selectSessionById = (state, sessionId) => {
  return state.chat.sessions[sessionId] || null;
};

export const selectAllSessions = state => {
  return Object.values(state.chat.sessions);
};

export const selectActiveSessions = state => {
  return Object.values(state.chat.sessions).filter(session => session.isActive);
};

// Thunks
export const initializeSession = (userId, userName) => async dispatch => {
  dispatch(setLoading(true));
  
  try {
    const response = await fetch('/api/chat/sessions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ userId, userName })
    });
    
    if (!response.ok) {
      throw new Error('Failed to initialize chat session');
    }
    
    const data = await response.json();
    
    dispatch(createSession({
      id: data.id,
      userId,
      userName,
      expiresAt: data.expiresAt
    }));
    
    dispatch(setLoading(false));
    return data.id;
  } catch (error) {
    dispatch(setError(error.message));
    return null;
  }
};

export const sendMessage = (sessionId, content) => async (dispatch, getState) => {
  const session = selectSessionById(getState(), sessionId);
  
  if (!session) {
    dispatch(setError('Session not found'));
    return;
  }
  
  // Optimistically add user message to state
  const userMessage = {
    id: `msg-${Date.now()}`,
    content,
    sender: {
      id: session.userId,
      name: session.userName,
      type: 'user'
    },
    timestamp: new Date().toISOString()
  };
  
  dispatch(addMessage({
    sessionId,
    message: userMessage
  }));
  
  dispatch(setTypingStatus({
    sessionId,
    isTyping: true
  }));
  
  try {
    const response = await fetch(`/api/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content })
    });
    
    if (!response.ok) {
      throw new Error('Failed to send message');
    }
    
    const data = await response.json();
    
    dispatch(setTypingStatus({
      sessionId,
      isTyping: false
    }));
    
    // Add AI response to state
    const aiMessage = {
      id: data.id,
      content: data.content,
      sender: {
        id: data.sender.id,
        name: data.sender.name,
        type: 'ai'
      },
      timestamp: data.timestamp
    };
    
    dispatch(addMessage({
      sessionId,
      message: aiMessage
    }));
  } catch (error) {
    dispatch(setTypingStatus({
      sessionId,
      isTyping: false
    }));
    dispatch(setError(error.message));
  }
};
