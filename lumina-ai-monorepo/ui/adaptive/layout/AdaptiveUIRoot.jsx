import React from 'react';
import PropTypes from 'prop-types';
import { useSelector, useDispatch } from 'react-redux';
import AdaptiveLayout from './AdaptiveLayout';
import NotificationProvider from '../notification/NotificationProvider';
import '../styles/AdaptiveUIRoot.css';

/**
 * AdaptiveUIRoot component serves as the root component for the Adaptive UI system.
 * It integrates all adaptive UI components and provides a consistent user experience.
 */
const AdaptiveUIRoot = ({ userId, userName, children }) => {
  const preferences = useSelector(state => state.preferences);
  const dispatch = useDispatch();
  
  // Handle theme toggle
  const handleThemeToggle = () => {
    const newTheme = preferences.appearance.theme === 'light' ? 'dark' : 'light';
    dispatch({
      type: 'preferences/updatePreference',
      payload: {
        category: 'appearance',
        key: 'theme',
        value: newTheme
      }
    });
  };
  
  // Sidebar content
  const sidebar = (
    <div className="adaptive-ui-sidebar">
      <div className="user-profile">
        <div className="user-avatar">
          {userName.charAt(0).toUpperCase()}
        </div>
        <div className="user-info">
          <div className="user-name">{userName}</div>
          <div className="user-id">ID: {userId}</div>
        </div>
      </div>
      
      <nav className="sidebar-navigation">
        <ul>
          <li className="nav-item active">
            <span className="nav-icon">💬</span>
            <span className="nav-text">Chat</span>
          </li>
          <li className="nav-item">
            <span className="nav-icon">🤝</span>
            <span className="nav-text">Collaboration</span>
          </li>
          <li className="nav-item">
            <span className="nav-icon">🔧</span>
            <span className="nav-text">Tools</span>
          </li>
          <li className="nav-item">
            <span className="nav-icon">⚙️</span>
            <span className="nav-text">Settings</span>
          </li>
        </ul>
      </nav>
    </div>
  );
  
  // Toolbar content
  const toolbar = (
    <div className="adaptive-ui-toolbar">
      <button 
        className="theme-toggle-button" 
        onClick={handleThemeToggle}
        aria-label={`Switch to ${preferences.appearance.theme === 'light' ? 'dark' : 'light'} theme`}
      >
        {preferences.appearance.theme === 'light' ? '🌙' : '☀️'}
      </button>
      
      <button className="font-size-button" aria-label="Adjust font size">
        Aa
      </button>
      
      <button className="help-button" aria-label="Help">
        ?
      </button>
    </div>
  );
  
  return (
    <div className={`adaptive-ui-root theme-${preferences.appearance.theme}`}>
      <NotificationProvider />
      
      <AdaptiveLayout
        title="Lumina AI"
        sidebar={sidebar}
        toolbar={toolbar}
      >
        {children}
      </AdaptiveLayout>
    </div>
  );
};

AdaptiveUIRoot.propTypes = {
  userId: PropTypes.string.isRequired,
  userName: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired
};

export default AdaptiveUIRoot;
