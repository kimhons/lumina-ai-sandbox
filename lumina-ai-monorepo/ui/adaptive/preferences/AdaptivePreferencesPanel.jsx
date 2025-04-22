import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useSelector, useDispatch } from 'react-redux';
import { updatePreference, updateCategory, resetCategory } from './preferencesSlice';
import '../styles/AdaptivePreferencesPanel.css';

/**
 * AdaptivePreferencesPanel component for allowing users to customize their UI experience.
 */
const AdaptivePreferencesPanel = ({ onClose }) => {
  const preferences = useSelector(state => state.preferences);
  const dispatch = useDispatch();
  
  const [activeTab, setActiveTab] = useState('appearance');
  const [tempPreferences, setTempPreferences] = useState(preferences);
  
  // Reset temp preferences when panel opens
  useEffect(() => {
    setTempPreferences(preferences);
  }, [preferences]);
  
  // Handle preference change
  const handlePreferenceChange = (category, key, value) => {
    setTempPreferences(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };
  
  // Apply changes
  const handleApply = () => {
    // Apply changes for each category
    Object.keys(tempPreferences).forEach(category => {
      if (JSON.stringify(preferences[category]) !== JSON.stringify(tempPreferences[category])) {
        dispatch(updateCategory({
          category,
          values: tempPreferences[category]
        }));
      }
    });
    
    onClose();
  };
  
  // Reset current category
  const handleReset = () => {
    dispatch(resetCategory({ category: activeTab }));
    setTempPreferences(prev => ({
      ...prev,
      [activeTab]: preferences[activeTab]
    }));
  };
  
  // Render appearance settings
  const renderAppearanceSettings = () => (
    <div className="preferences-section">
      <div className="preference-group">
        <h3>Theme</h3>
        <div className="preference-controls">
          <label className="radio-label">
            <input
              type="radio"
              name="theme"
              value="light"
              checked={tempPreferences.appearance.theme === 'light'}
              onChange={() => handlePreferenceChange('appearance', 'theme', 'light')}
            />
            Light
          </label>
          <label className="radio-label">
            <input
              type="radio"
              name="theme"
              value="dark"
              checked={tempPreferences.appearance.theme === 'dark'}
              onChange={() => handlePreferenceChange('appearance', 'theme', 'dark')}
            />
            Dark
          </label>
          <label className="radio-label">
            <input
              type="radio"
              name="theme"
              value="system"
              checked={tempPreferences.appearance.theme === 'system'}
              onChange={() => handlePreferenceChange('appearance', 'theme', 'system')}
            />
            System
          </label>
        </div>
      </div>
      
      <div className="preference-group">
        <h3>Font Size</h3>
        <div className="preference-controls">
          <label className="radio-label">
            <input
              type="radio"
              name="fontSize"
              value="small"
              checked={tempPreferences.appearance.fontSize === 'small'}
              onChange={() => handlePreferenceChange('appearance', 'fontSize', 'small')}
            />
            Small
          </label>
          <label className="radio-label">
            <input
              type="radio"
              name="fontSize"
              value="medium"
              checked={tempPreferences.appearance.fontSize === 'medium'}
              onChange={() => handlePreferenceChange('appearance', 'fontSize', 'medium')}
            />
            Medium
          </label>
          <label className="radio-label">
            <input
              type="radio"
              name="fontSize"
              value="large"
              checked={tempPreferences.appearance.fontSize === 'large'}
              onChange={() => handlePreferenceChange('appearance', 'fontSize', 'large')}
            />
            Large
          </label>
        </div>
      </div>
      
      <div className="preference-group">
        <h3>Accessibility</h3>
        <div className="preference-controls">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={tempPreferences.appearance.highContrast}
              onChange={() => handlePreferenceChange('appearance', 'highContrast', !tempPreferences.appearance.highContrast)}
            />
            High Contrast
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={tempPreferences.appearance.reducedMotion}
              onChange={() => handlePreferenceChange('appearance', 'reducedMotion', !tempPreferences.appearance.reducedMotion)}
            />
            Reduced Motion
          </label>
        </div>
      </div>
    </div>
  );
  
  // Render notification settings
  const renderNotificationSettings = () => (
    <div className="preferences-section">
      <div className="preference-group">
        <h3>Notification Types</h3>
        <div className="preference-controls">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={tempPreferences.notifications.chatTerminationWarnings}
              onChange={() => handlePreferenceChange('notifications', 'chatTerminationWarnings', !tempPreferences.notifications.chatTerminationWarnings)}
            />
            Chat Termination Warnings
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={tempPreferences.notifications.collaborationInvites}
              onChange={() => handlePreferenceChange('notifications', 'collaborationInvites', !tempPreferences.notifications.collaborationInvites)}
            />
            Collaboration Invites
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={tempPreferences.notifications.systemUpdates}
              onChange={() => handlePreferenceChange('notifications', 'systemUpdates', !tempPreferences.notifications.systemUpdates)}
            />
            System Updates
          </label>
        </div>
      </div>
      
      <div className="preference-group">
        <h3>Sound</h3>
        <div className="preference-controls">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={tempPreferences.notifications.soundForNotifications}
              onChange={() => handlePreferenceChange('notifications', 'soundForNotifications', !tempPreferences.notifications.soundForNotifications)}
            />
            Play Sound for Notifications
          </label>
        </div>
      </div>
    </div>
  );
  
  // Render privacy settings
  const renderPrivacySettings = () => (
    <div className="preferences-section">
      <div className="preference-group">
        <h3>Data Usage</h3>
        <div className="preference-controls">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={tempPreferences.privacy.shareAnalytics}
              onChange={() => handlePreferenceChange('privacy', 'shareAnalytics', !tempPreferences.privacy.shareAnalytics)}
            />
            Share Analytics
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={tempPreferences.privacy.storeHistory}
              onChange={() => handlePreferenceChange('privacy', 'storeHistory', !tempPreferences.privacy.storeHistory)}
            />
            Store Chat History
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={tempPreferences.privacy.personalizedSuggestions}
              onChange={() => handlePreferenceChange('privacy', 'personalizedSuggestions', !tempPreferences.privacy.personalizedSuggestions)}
            />
            Personalized Suggestions
          </label>
        </div>
      </div>
    </div>
  );
  
  return (
    <div className="adaptive-preferences-panel">
      <div className="preferences-header">
        <h2>Preferences</h2>
        <button className="close-button" onClick={onClose}>×</button>
      </div>
      
      <div className="preferences-tabs">
        <button 
          className={`tab-button ${activeTab === 'appearance' ? 'active' : ''}`}
          onClick={() => setActiveTab('appearance')}
        >
          Appearance
        </button>
        <button 
          className={`tab-button ${activeTab === 'notifications' ? 'active' : ''}`}
          onClick={() => setActiveTab('notifications')}
        >
          Notifications
        </button>
        <button 
          className={`tab-button ${activeTab === 'privacy' ? 'active' : ''}`}
          onClick={() => setActiveTab('privacy')}
        >
          Privacy
        </button>
      </div>
      
      <div className="preferences-content">
        {activeTab === 'appearance' && renderAppearanceSettings()}
        {activeTab === 'notifications' && renderNotificationSettings()}
        {activeTab === 'privacy' && renderPrivacySettings()}
      </div>
      
      <div className="preferences-footer">
        <button className="reset-button" onClick={handleReset}>
          Reset
        </button>
        <div className="footer-actions">
          <button className="cancel-button" onClick={onClose}>
            Cancel
          </button>
          <button className="apply-button" onClick={handleApply}>
            Apply
          </button>
        </div>
      </div>
    </div>
  );
};

AdaptivePreferencesPanel.propTypes = {
  onClose: PropTypes.func.isRequired
};

export default AdaptivePreferencesPanel;
