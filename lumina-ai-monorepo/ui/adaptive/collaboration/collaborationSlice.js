import { createSlice } from '@reduxjs/toolkit';

/**
 * Redux slice for managing collaboration features in the Adaptive UI system.
 */
const collaborationSlice = createSlice({
  name: 'collaboration',
  initialState: {
    sessions: {},
    activeSessionId: null,
    isConnected: false,
    connectionError: null
  },
  reducers: {
    createSession: (state, action) => {
      const { id, title, type, participants } = action.payload;
      state.sessions[id] = {
        id,
        title,
        type,
        participants,
        createdAt: new Date().toISOString(),
        actions: []
      };
      state.activeSessionId = id;
    },
    setActiveSession: (state, action) => {
      state.activeSessionId = action.payload;
    },
    addParticipant: (state, action) => {
      const { sessionId, participant } = action.payload;
      if (state.sessions[sessionId]) {
        state.sessions[sessionId].participants.push(participant);
      }
    },
    removeParticipant: (state, action) => {
      const { sessionId, participantId } = action.payload;
      if (state.sessions[sessionId]) {
        state.sessions[sessionId].participants = state.sessions[sessionId].participants.filter(
          p => p.id !== participantId
        );
      }
    },
    addAction: (state, action) => {
      const { sessionId, action: collaborationAction } = action.payload;
      if (state.sessions[sessionId]) {
        state.sessions[sessionId].actions.push({
          ...collaborationAction,
          timestamp: new Date().toISOString()
        });
      }
    },
    setConnectionStatus: (state, action) => {
      state.isConnected = action.payload;
      if (action.payload) {
        state.connectionError = null;
      }
    },
    setConnectionError: (state, action) => {
      state.connectionError = action.payload;
      state.isConnected = false;
    },
    closeSession: (state, action) => {
      const sessionId = action.payload;
      delete state.sessions[sessionId];
      if (state.activeSessionId === sessionId) {
        state.activeSessionId = Object.keys(state.sessions)[0] || null;
      }
    }
  }
});

export const {
  createSession,
  setActiveSession,
  addParticipant,
  removeParticipant,
  addAction,
  setConnectionStatus,
  setConnectionError,
  closeSession
} = collaborationSlice.actions;

export default collaborationSlice.reducer;

// Selectors
export const selectActiveSession = state => {
  const activeSessionId = state.collaboration.activeSessionId;
  return activeSessionId ? state.collaboration.sessions[activeSessionId] : null;
};

export const selectSessionById = (state, sessionId) => {
  return state.collaboration.sessions[sessionId] || null;
};

export const selectAllSessions = state => {
  return Object.values(state.collaboration.sessions);
};

// Thunks
export const createCaptchaBypassSession = (userId, userName, agentId, agentName) => dispatch => {
  const sessionId = `session-${Date.now()}`;
  
  dispatch(createSession({
    id: sessionId,
    title: 'CAPTCHA Assistance',
    type: 'captcha-bypass',
    participants: [
      { id: userId, name: userName, role: 'user' },
      { id: agentId, name: agentName, role: 'agent' }
    ]
  }));
  
  return sessionId;
};
