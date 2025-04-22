import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import styled from 'styled-components';
import PropTypes from 'prop-types';
import { selectTheme } from '../preferences/preferencesSlice';
import AdaptiveLayout from './AdaptiveLayout';
import ChatProvider from '../chat/ChatProvider';
import PreferencesProvider from '../preferences/PreferencesProvider';
import { CaptchaBypassCollaboration } from '../collaboration/CaptchaBypassCollaboration';
import { CollaborationWorkspace } from '../collaboration/CollaborationWorkspace';

// Import existing UI components
import AgentActivityPanel from '../../../shared/AgentActivityPanel';
import EnhancedAgentActivityPanel from '../../../shared/EnhancedAgentActivityPanel';
import CollaborativeWorkspace from '../../../shared/CollaborativeWorkspace';
import EnhancedCollaborativeWorkspace from '../../../shared/EnhancedCollaborativeWorkspace';
import MemoryVisualization from '../../../shared/MemoryVisualization';
import ToolIntegrationUI from '../../../shared/ToolIntegrationUI';

// Styled components
const SidebarContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const SidebarSection = styled.div`
  margin-bottom: 16px;
`;

const SidebarHeader = styled.h3`
  font-size: 16px;
  font-weight: 600;
  margin: 16px 16px 8px;
  color: ${props => props.theme === 'dark' ? '#FFFFFF' : '#333333'};
`;

const SidebarItem = styled.div`
  padding: 10px 16px;
  cursor: pointer;
  border-radius: 6px;
  margin: 2px 8px;
  font-size: 14px;
  color: ${props => props.theme === 'dark' ? '#FFFFFF' : '#333333'};
  background-color: ${props => props.active 
    ? props.theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'
    : 'transparent'
  };
  
  &:hover {
    background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.03)'};
  }
`;

const ToolbarButton = styled.button`
  background: transparent;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: ${props => props.theme === 'dark' ? '#FFFFFF' : '#333333'};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  
  &:hover {
    background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.03)'};
  }
  
  svg {
    width: 16px;
    height: 16px;
  }
`;

const ToolbarSeparator = styled.div`
  width: 1px;
  height: 24px;
  background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'};
  margin: 0 8px;
`;

const ToolbarSpacer = styled.div`
  flex: 1;
`;

/**
 * AdaptiveUIIntegration Component
 * 
 * Integrates the new adaptive UI components with existing UI components
 * to provide a seamless user experience.
 */
const AdaptiveUIIntegration = ({
  userId,
  userName,
  initialView = 'chat'
}) => {
  const dispatch = useDispatch();
  const theme = useSelector(selectTheme);
  const [activeView, setActiveView] = useState(initialView);
  const [activeChatId, setActiveChatId] = useState(null);
  const [showPreferences, setShowPreferences] = useState(false);
  
  // Generate a new chat session ID
  const generateChatId = () => {
    return `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  };
  
  // Create a new chat session
  const handleNewChat = () => {
    const newChatId = generateChatId();
    setActiveChatId(newChatId);
    setActiveView('chat');
  };
  
  // Render sidebar content
  const renderSidebar = () => {
    return (
      <SidebarContainer>
        <SidebarHeader theme={theme}>Workspaces</SidebarHeader>
        <SidebarSection>
          <SidebarItem 
            theme={theme} 
            active={activeView === 'chat'} 
            onClick={() => setActiveView('chat')}
          >
            Chat
          </SidebarItem>
          <SidebarItem 
            theme={theme} 
            active={activeView === 'collaboration'} 
            onClick={() => setActiveView('collaboration')}
          >
            Collaboration
          </SidebarItem>
          <SidebarItem 
            theme={theme} 
            active={activeView === 'captcha'} 
            onClick={() => setActiveView('captcha')}
          >
            CAPTCHA Assistance
          </SidebarItem>
        </SidebarSection>
        
        <SidebarHeader theme={theme}>Tools</SidebarHeader>
        <SidebarSection>
          <SidebarItem 
            theme={theme} 
            active={activeView === 'memory'} 
            onClick={() => setActiveView('memory')}
          >
            Memory Visualization
          </SidebarItem>
          <SidebarItem 
            theme={theme} 
            active={activeView === 'tools'} 
            onClick={() => setActiveView('tools')}
          >
            Tool Integration
          </SidebarItem>
          <SidebarItem 
            theme={theme} 
            active={activeView === 'activity'} 
            onClick={() => setActiveView('activity')}
          >
            Agent Activity
          </SidebarItem>
        </SidebarSection>
      </SidebarContainer>
    );
  };
  
  // Render toolbar content
  const renderToolbar = () => {
    return (
      <>
        <ToolbarButton theme={theme} onClick={handleNewChat}>
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 13H13V19H11V13H5V11H11V5H13V11H19V13Z" fill="currentColor"/>
          </svg>
          New Chat
        </ToolbarButton>
        
        <ToolbarSeparator theme={theme} />
        
        <ToolbarButton theme={theme}>
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 1H4C2.9 1 2 1.9 2 3V17H4V3H16V1ZM19 5H8C6.9 5 6 5.9 6 7V21C6 22.1 6.9 23 8 23H19C20.1 23 21 22.1 21 21V7C21 5.9 20.1 5 19 5ZM19 21H8V7H19V21Z" fill="currentColor"/>
          </svg>
          Copy
        </ToolbarButton>
        
        <ToolbarButton theme={theme}>
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12V19H5V12H3V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V12H19ZM13 12.67L15.59 10.09L17 11.5L12 16.5L7 11.5L8.41 10.09L11 12.67V3H13V12.67Z" fill="currentColor"/>
          </svg>
          Export
        </ToolbarButton>
        
        <ToolbarSpacer />
        
        <ToolbarButton theme={theme} onClick={() => setShowPreferences(true)}>
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19.14 12.94C19.18 12.64 19.2 12.33 19.2 12C19.2 11.68 19.18 11.36 19.13 11.06L21.16 9.48C21.34 9.34 21.39 9.07 21.28 8.87L19.36 5.55C19.24 5.33 18.99 5.26 18.77 5.33L16.38 6.29C15.88 5.91 15.35 5.59 14.76 5.35L14.4 2.81C14.36 2.57 14.16 2.4 13.92 2.4H10.08C9.84 2.4 9.65 2.57 9.61 2.81L9.25 5.35C8.66 5.59 8.12 5.92 7.63 6.29L5.24 5.33C5.02 5.25 4.77 5.33 4.65 5.55L2.74 8.87C2.62 9.08 2.66 9.34 2.86 9.48L4.89 11.06C4.84 11.36 4.8 11.69 4.8 12C4.8 12.31 4.82 12.64 4.87 12.94L2.84 14.52C2.66 14.66 2.61 14.93 2.72 15.13L4.64 18.45C4.76 18.67 5.01 18.74 5.23 18.67L7.62 17.71C8.12 18.09 8.65 18.41 9.24 18.65L9.6 21.19C9.65 21.43 9.84 21.6 10.08 21.6H13.92C14.16 21.6 14.36 21.43 14.39 21.19L14.75 18.65C15.34 18.41 15.88 18.09 16.37 17.71L18.76 18.67C18.98 18.75 19.23 18.67 19.35 18.45L21.27 15.13C21.39 14.91 21.34 14.66 21.15 14.52L19.14 12.94ZM12 15.6C10.02 15.6 8.4 13.98 8.4 12C8.4 10.02 10.02 8.4 12 8.4C13.98 8.4 15.6 10.02 15.6 12C15.6 13.98 13.98 15.6 12 15.6Z" fill="currentColor"/>
          </svg>
          Preferences
        </ToolbarButton>
      </>
    );
  };
  
  // Render main content based on active view
  const renderContent = () => {
    switch (activeView) {
      case 'chat':
        return (
          <ChatProvider
            sessionId={activeChatId || generateChatId()}
            userId={userId}
            userName={userName}
            aiName="Lumina AI"
            title="Chat"
            onSessionEnd={() => {}}
          />
        );
        
      case 'collaboration':
        return (
          <CollaborationWorkspace
            userId={userId}
            userName={userName}
          />
        );
        
      case 'captcha':
        return (
          <CaptchaBypassCollaboration
            userId={userId}
            userName={userName}
          />
        );
        
      case 'memory':
        return <MemoryVisualization />;
        
      case 'tools':
        return <ToolIntegrationUI />;
        
      case 'activity':
        return <EnhancedAgentActivityPanel />;
        
      default:
        return (
          <div>
            <h3>Select a workspace or tool from the sidebar</h3>
          </div>
        );
    }
  };
  
  // Render preferences panel if shown
  if (showPreferences) {
    return (
      <PreferencesProvider
        onClose={() => setShowPreferences(false)}
      />
    );
  }
  
  return (
    <AdaptiveLayout
      title="Lumina AI"
      sidebar={renderSidebar()}
      toolbar={renderToolbar()}
    >
      {renderContent()}
    </AdaptiveLayout>
  );
};

AdaptiveUIIntegration.propTypes = {
  userId: PropTypes.string.isRequired,
  userName: PropTypes.string,
  initialView: PropTypes.string
};

export default AdaptiveUIIntegration;
