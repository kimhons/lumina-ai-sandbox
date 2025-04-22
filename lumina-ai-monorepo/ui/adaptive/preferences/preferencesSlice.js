import { createSlice } from '@reduxjs/toolkit';

/**
 * Redux slice for managing user preferences in the Adaptive UI system.
 */
const preferencesSlice = createSlice({
  name: 'preferences',
  initialState: {
    appearance: {
      theme: 'light',
      fontSize: 'medium',
      accentColor: '#007AFF',
      highContrast: false,
      reducedMotion: false
    },
    behavior: {
      autoScrollEnabled: true,
      soundEnabled: true,
      notificationsEnabled: true,
      confirmDialogsEnabled: true
    },
    accessibility: {
      screenReaderOptimized: false,
      keyboardNavigationMode: 'standard',
      colorBlindMode: 'none'
    },
    notifications: {
      chatTerminationWarnings: true,
      collaborationInvites: true,
      systemUpdates: true,
      soundForNotifications: true
    },
    privacy: {
      shareAnalytics: true,
      storeHistory: true,
      personalizedSuggestions: true
    }
  },
  reducers: {
    updatePreference: (state, action) => {
      const { category, key, value } = action.payload;
      if (state[category] && key in state[category]) {
        state[category][key] = value;
      }
    },
    updateCategory: (state, action) => {
      const { category, values } = action.payload;
      if (state[category]) {
        state[category] = {
          ...state[category],
          ...values
        };
      }
    },
    resetCategory: (state, action) => {
      const { category } = action.payload;
      if (category === 'all') {
        return preferencesSlice.getInitialState();
      } else if (state[category]) {
        state[category] = preferencesSlice.getInitialState()[category];
      }
    },
    importPreferences: (state, action) => {
      return {
        ...state,
        ...action.payload
      };
    }
  }
});

export const {
  updatePreference,
  updateCategory,
  resetCategory,
  importPreferences
} = preferencesSlice.actions;

export default preferencesSlice.reducer;

// Selectors
export const selectAppearance = state => state.preferences.appearance;
export const selectBehavior = state => state.preferences.behavior;
export const selectAccessibility = state => state.preferences.accessibility;
export const selectNotificationPreferences = state => state.preferences.notifications;
export const selectPrivacy = state => state.preferences.privacy;

// Thunks
export const toggleTheme = () => (dispatch, getState) => {
  const currentTheme = selectAppearance(getState()).theme;
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  
  dispatch(updatePreference({
    category: 'appearance',
    key: 'theme',
    value: newTheme
  }));
};

export const setAccessibilityMode = (mode) => dispatch => {
  switch (mode) {
    case 'screenReader':
      dispatch(updateCategory({
        category: 'accessibility',
        values: {
          screenReaderOptimized: true,
          keyboardNavigationMode: 'enhanced'
        }
      }));
      break;
    case 'colorBlind':
      dispatch(updateCategory({
        category: 'accessibility',
        values: {
          colorBlindMode: 'deuteranopia'
        }
      }));
      break;
    case 'reducedMotion':
      dispatch(updatePreference({
        category: 'appearance',
        key: 'reducedMotion',
        value: true
      }));
      break;
    case 'highContrast':
      dispatch(updatePreference({
        category: 'appearance',
        key: 'highContrast',
        value: true
      }));
      break;
    default:
      // Reset to standard mode
      dispatch(resetCategory({
        category: 'accessibility'
      }));
      dispatch(updatePreference({
        category: 'appearance',
        key: 'reducedMotion',
        value: false
      }));
      dispatch(updatePreference({
        category: 'appearance',
        key: 'highContrast',
        value: false
      }));
  }
};
