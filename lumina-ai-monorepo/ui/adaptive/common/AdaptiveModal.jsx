import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { useSelector } from 'react-redux';
import { selectTheme } from '../preferences/preferencesSlice';

// Styled components
const Container = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: ${props => props.theme === 'dark' ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.8)'};
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: ${props => props.show ? 1 : 0};
  visibility: ${props => props.show ? 'visible' : 'hidden'};
  transition: opacity 0.3s ease, visibility 0.3s ease;
`;

const ModalContent = styled.div`
  background-color: ${props => props.theme === 'dark' ? '#1E1E1E' : '#FFFFFF'};
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  width: ${props => props.width || '500px'};
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transform: ${props => props.show ? 'translateY(0)' : 'translateY(20px)'};
  transition: transform 0.3s ease;
`;

const ModalHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'};
`;

const ModalTitle = styled.h3`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: ${props => props.theme === 'dark' ? '#FFFFFF' : '#333333'};
`;

const CloseButton = styled.button`
  background: transparent;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.theme === 'dark' ? '#BBBBBB' : '#666666'};
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'};
    color: ${props => props.theme === 'dark' ? '#FFFFFF' : '#333333'};
  }
  
  svg {
    width: 20px;
    height: 20px;
  }
`;

const ModalBody = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: ${props => props.padding || '20px'};
  
  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)'};
    border-radius: 20px;
  }
`;

const ModalFooter = styled.div`
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'};
  gap: 12px;
`;

const Button = styled.button`
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  
  background-color: ${props => props.primary ? '#007AFF' : 'transparent'};
  color: ${props => props.primary ? '#FFFFFF' : props.theme === 'dark' ? '#FFFFFF' : '#333333'};
  border: ${props => props.primary ? 'none' : props.theme === 'dark' ? '1px solid rgba(255, 255, 255, 0.2)' : '1px solid rgba(0, 0, 0, 0.2)'};
  
  &:hover {
    background-color: ${props => props.primary ? '#0066CC' : props.theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'};
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

/**
 * AdaptiveModal Component
 * 
 * A reusable modal component that adapts to the current theme and provides
 * a consistent interface for displaying modal content.
 */
const AdaptiveModal = ({
  show,
  onClose,
  title,
  children,
  width,
  padding,
  footer,
  closeOnBackdropClick = true
}) => {
  const theme = useSelector(selectTheme);
  
  // Handle backdrop click
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget && closeOnBackdropClick) {
      onClose();
    }
  };
  
  return (
    <Container 
      show={show} 
      theme={theme} 
      onClick={handleBackdropClick}
    >
      <ModalContent show={show} theme={theme} width={width}>
        <ModalHeader theme={theme}>
          <ModalTitle theme={theme}>{title}</ModalTitle>
          <CloseButton theme={theme} onClick={onClose} aria-label="Close">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" fill="currentColor"/>
            </svg>
          </CloseButton>
        </ModalHeader>
        
        <ModalBody theme={theme} padding={padding}>
          {children}
        </ModalBody>
        
        {footer && (
          <ModalFooter theme={theme}>
            {footer}
          </ModalFooter>
        )}
      </ModalContent>
    </Container>
  );
};

AdaptiveModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  width: PropTypes.string,
  padding: PropTypes.string,
  footer: PropTypes.node,
  closeOnBackdropClick: PropTypes.bool
};

export default AdaptiveModal;
