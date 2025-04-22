import React from 'react';
import PropTypes from 'prop-types';
import { useSelector, useDispatch } from 'react-redux';
import '../styles/AdaptiveUIBridge.css';

/**
 * AdaptiveUIBridge component for integrating the Adaptive UI system with existing UI components.
 * This component serves as a bridge between the new adaptive components and legacy components.
 */
const AdaptiveUIBridge = ({ legacyComponent, adaptiveProps }) => {
  const preferences = useSelector(state => state.preferences);
  const dispatch = useDispatch();
  
  // Apply adaptive styling to legacy component wrapper
  const getAdaptiveStyles = () => {
    const { theme, fontSize, highContrast } = preferences.appearance;
    
    return {
      fontSize: `${fontSize === 'large' ? 1.2 : fontSize === 'small' ? 0.9 : 1}rem`,
      backgroundColor: theme === 'dark' ? '#1a1a1a' : '#ffffff',
      color: theme === 'dark' ? '#ffffff' : '#1a1a1a',
      filter: highContrast ? 'contrast(1.5)' : 'none'
    };
  };
  
  // Handle events from legacy components and translate them to adaptive actions
  const handleLegacyEvent = (event, data) => {
    switch (event) {
      case 'notification':
        dispatch({
          type: 'notifications/addNotification',
          payload: {
            type: data.type || 'info',
            title: data.title || 'Notification',
            message: data.message,
            closable: true,
            duration: data.duration || 5000
          }
        });
        break;
        
      case 'themeChange':
        dispatch({
          type: 'preferences/updatePreference',
          payload: {
            category: 'appearance',
            key: 'theme',
            value: data.theme
          }
        });
        break;
        
      case 'error':
        dispatch({
          type: 'notifications/addNotification',
          payload: {
            type: 'error',
            title: 'Error',
            message: data.message,
            closable: true,
            duration: 0
          }
        });
        break;
        
      default:
        console.log('Unknown legacy event:', event, data);
    }
  };
  
  // Create enhanced props for legacy component
  const enhancedProps = {
    ...adaptiveProps,
    theme: preferences.appearance.theme,
    fontSize: preferences.appearance.fontSize,
    onEvent: handleLegacyEvent
  };
  
  return (
    <div className="adaptive-ui-bridge" style={getAdaptiveStyles()}>
      {React.cloneElement(legacyComponent, enhancedProps)}
    </div>
  );
};

AdaptiveUIBridge.propTypes = {
  legacyComponent: PropTypes.element.isRequired,
  adaptiveProps: PropTypes.object
};

AdaptiveUIBridge.defaultProps = {
  adaptiveProps: {}
};

export default AdaptiveUIBridge;
