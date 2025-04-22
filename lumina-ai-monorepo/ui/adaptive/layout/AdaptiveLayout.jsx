import React from 'react';
import PropTypes from 'prop-types';
import { useSelector } from 'react-redux';
import '../styles/AdaptiveLayout.css';

/**
 * AdaptiveLayout component for providing a responsive and adaptive layout
 * that adjusts based on user preferences and device capabilities.
 */
const AdaptiveLayout = ({ title, sidebar, toolbar, children }) => {
  const preferences = useSelector(state => state.preferences);
  const { theme, fontSize, reducedMotion, highContrast } = preferences.appearance;
  
  // Determine layout class based on preferences
  const getLayoutClasses = () => {
    const classes = [`theme-${theme}`];
    
    if (reducedMotion) classes.push('reduced-motion');
    if (highContrast) classes.push('high-contrast');
    
    return classes.join(' ');
  };
  
  return (
    <div className={`adaptive-layout ${getLayoutClasses()}`}>
      <header className="adaptive-layout-header">
        <h1 className="adaptive-layout-title">{title}</h1>
        <div className="adaptive-layout-toolbar">
          {toolbar}
        </div>
      </header>
      
      <div className="adaptive-layout-content">
        <aside className="adaptive-layout-sidebar">
          {sidebar}
        </aside>
        
        <main 
          className="adaptive-layout-main"
          style={{ fontSize: `${fontSize === 'large' ? 1.2 : fontSize === 'small' ? 0.9 : 1}rem` }}
        >
          {children}
        </main>
      </div>
    </div>
  );
};

AdaptiveLayout.propTypes = {
  title: PropTypes.string.isRequired,
  sidebar: PropTypes.node,
  toolbar: PropTypes.node,
  children: PropTypes.node.isRequired
};

export default AdaptiveLayout;
