import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { useSelector } from 'react-redux';
import { selectTheme } from '../preferences/preferencesSlice';

// Styled components
const Container = styled.div`
  position: fixed;
  bottom: ${props => props.position === 'bottom' ? '20px' : 'auto'};
  top: ${props => props.position === 'top' ? '20px' : 'auto'};
  left: ${props => props.position === 'left' || props.position === 'bottom' || props.position === 'top' ? '20px' : 'auto'};
  right: ${props => props.position === 'right' ? '20px' : 'auto'};
  z-index: 1000;
  max-width: 90vw;
  width: ${props => props.width || 'auto'};
`;

const ToastContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const Toast = styled.div`
  background-color: ${props => {
    if (props.theme === 'dark') {
      switch (props.type) {
        case 'success': return '#34C759';
        case 'error': return '#FF3B30';
        case 'warning': return '#FF9500';
        case 'info': return '#0A84FF';
        default: return '#2C2C2E';
      }
    } else {
      switch (props.type) {
        case 'success': return '#34C759';
        case 'error': return '#FF3B30';
        case 'warning': return '#FF9500';
        case 'info': return '#0A84FF';
        default: return '#FFFFFF';
      }
    }
  }};
  color: ${props => {
    if (props.type === 'success' || props.type === 'error' || props.type === 'warning' || props.type === 'info') {
      return '#FFFFFF';
    }
    return props.theme === 'dark' ? '#FFFFFF' : '#333333';
  }};
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 12px;
  animation: ${props => props.animation || 'slideIn'} 0.3s ease;
  max-width: 100%;
  
  @keyframes slideIn {
    from { transform: translateX(-100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  
  @keyframes slideUp {
    from { transform: translateY(100%); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
`;

const IconContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  svg {
    width: 20px;
    height: 20px;
  }
`;

const Content = styled.div`
  flex: 1;
  min-width: 0;
`;

const Title = styled.div`
  font-weight: 600;
  font-size: 14px;
  margin-bottom: ${props => props.message ? '4px' : '0'};
`;

const Message = styled.div`
  font-size: 13px;
  opacity: 0.9;
`;

const CloseButton = styled.button`
  background: transparent;
  border: none;
  color: inherit;
  opacity: 0.7;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  &:hover {
    opacity: 1;
  }
  
  svg {
    width: 16px;
    height: 16px;
  }
`;

const ActionButton = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: inherit;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }
`;

/**
 * AdaptiveNotification Component
 * 
 * A notification system that displays toast messages and adapts to the current theme.
 * Supports different types of notifications (success, error, warning, info) and
 * customizable positions.
 */
const AdaptiveNotification = ({
  notifications = [],
  position = 'bottom',
  width = '350px',
  animation = 'slideIn',
  onClose,
  onAction
}) => {
  const theme = useSelector(selectTheme);
  
  // Get icon based on notification type
  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return (
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 16.2L4.8 12L3.4 13.4L9 19L21 7L19.6 5.6L9 16.2Z" fill="currentColor"/>
          </svg>
        );
      case 'error':
        return (
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" fill="currentColor"/>
          </svg>
        );
      case 'warning':
        return (
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 21H23L12 2L1 21ZM13 18H11V16H13V18ZM13 14H11V10H13V14Z" fill="currentColor"/>
          </svg>
        );
      case 'info':
        return (
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V11H13V17ZM13 9H11V7H13V9Z" fill="currentColor"/>
          </svg>
        );
      default:
        return null;
    }
  };
  
  // Get animation based on position
  const getAnimation = () => {
    if (animation !== 'auto') return animation;
    
    switch (position) {
      case 'top':
      case 'bottom':
        return 'slideUp';
      case 'left':
        return 'slideIn';
      case 'right':
        return 'slideIn';
      default:
        return 'fadeIn';
    }
  };
  
  return (
    <Container position={position} width={width}>
      <ToastContainer>
        {notifications.map((notification) => (
          <Toast
            key={notification.id}
            theme={theme}
            type={notification.type}
            animation={getAnimation()}
          >
            {getIcon(notification.type) && (
              <IconContainer>
                {getIcon(notification.type)}
              </IconContainer>
            )}
            
            <Content>
              <Title message={notification.message}>{notification.title}</Title>
              {notification.message && (
                <Message>{notification.message}</Message>
              )}
            </Content>
            
            {notification.action && (
              <ActionButton 
                onClick={() => onAction(notification.id, notification.action)}
              >
                {notification.actionText || 'Action'}
              </ActionButton>
            )}
            
            {notification.closable !== false && (
              <CloseButton 
                onClick={() => onClose(notification.id)}
                aria-label="Close notification"
              >
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" fill="currentColor"/>
                </svg>
              </CloseButton>
            )}
          </Toast>
        ))}
      </ToastContainer>
    </Container>
  );
};

AdaptiveNotification.propTypes = {
  notifications: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      type: PropTypes.oneOf(['success', 'error', 'warning', 'info', 'default']),
      title: PropTypes.string.isRequired,
      message: PropTypes.string,
      closable: PropTypes.bool,
      action: PropTypes.string,
      actionText: PropTypes.string
    })
  ),
  position: PropTypes.oneOf(['top', 'bottom', 'left', 'right']),
  width: PropTypes.string,
  animation: PropTypes.oneOf(['slideIn', 'slideUp', 'fadeIn', 'auto']),
  onClose: PropTypes.func.isRequired,
  onAction: PropTypes.func
};

export default AdaptiveNotification;
