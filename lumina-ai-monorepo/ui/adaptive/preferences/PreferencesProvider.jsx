import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import styled from 'styled-components';
import PropTypes from 'prop-types';
import { 
  updatePreference, 
  resetPreferences, 
  savePreferencesToStorage,
  loadPreferencesFromStorage,
  selectTheme
} from './preferencesSlice';
import AdaptivePreferencesPanel from './AdaptivePreferencesPanel';

/**
 * PreferencesProvider Component
 * 
 * A wrapper component that connects the AdaptivePreferencesPanel to Redux state
 * and provides preference management functionality.
 */
const PreferencesProvider = ({ onClose }) => {
  const dispatch = useDispatch();
  const theme = useSelector(selectTheme);
  const preferences = useSelector(state => state.preferences);
  
  // Load preferences from storage on mount
  useEffect(() => {
    dispatch(loadPreferencesFromStorage());
  }, [dispatch]);
  
  // Handle theme change
  const handleThemeChange = (newTheme) => {
    dispatch(updatePreference({
      category: 'appearance',
      setting: 'theme',
      value: newTheme
    }));
  };
  
  // Handle preferences change
  const handlePreferencesChange = (updatedPreferences) => {
    // Update each category
    Object.keys(updatedPreferences).forEach(category => {
      Object.keys(updatedPreferences[category]).forEach(setting => {
        const value = updatedPreferences[category][setting];
        
        dispatch(updatePreference({
          category,
          setting,
          value
        }));
      });
    });
    
    // Save to storage
    dispatch(savePreferencesToStorage());
  };
  
  return (
    <AdaptivePreferencesPanel
      theme={theme}
      onThemeChange={handleThemeChange}
      onPreferencesChange={handlePreferencesChange}
      initialPreferences={preferences}
    />
  );
};

PreferencesProvider.propTypes = {
  onClose: PropTypes.func
};

export default PreferencesProvider;
