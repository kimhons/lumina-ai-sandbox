import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import AdaptiveNotification from '../notification/AdaptiveNotification';
import NotificationProvider from '../notification/NotificationProvider';
import AdaptiveLayout from '../layout/AdaptiveLayout';
import CaptchaBypassCollaboration from '../collaboration/CaptchaBypassCollaboration';
import CollaborationWorkspace from '../collaboration/CollaborationWorkspace';

const mockStore = configureStore([thunk]);

describe('Adaptive UI Components', () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      notifications: {
        items: [
          {
            id: 'notification-1',
            type: 'warning',
            title: 'Chat Session Ending Soon',
            message: 'This chat session will terminate in 30 seconds.',
            action: 'extendSession',
            actionText: 'Extend Session',
            closable: true,
            duration: 0
          }
        ]
      },
      preferences: {
        appearance: {
          theme: 'light',
          fontSize: 'medium',
          accentColor: '#007AFF'
        },
        behavior: {
          autoScrollEnabled: true,
          soundEnabled: true
        },
        accessibility: {
          highContrast: false,
          reducedMotion: false
        }
      },
      collaboration: {
        sessions: {
          'session-1': {
            id: 'session-1',
            title: 'CAPTCHA Assistance',
            type: 'captcha-bypass',
            participants: [
              { id: 'user-1', name: 'John Doe', role: 'user' },
              { id: 'agent-1', name: 'Lumina AI', role: 'agent' }
            ],
            actions: []
          }
        },
        activeSessionId: 'session-1'
      }
    });
  });

  test('AdaptiveNotification renders correctly', () => {
    const notification = {
      id: 'notification-1',
      type: 'warning',
      title: 'Chat Session Ending Soon',
      message: 'This chat session will terminate in 30 seconds.',
      action: 'extendSession',
      actionText: 'Extend Session',
      closable: true,
      duration: 0
    };

    const handleAction = jest.fn();
    const handleClose = jest.fn();

    render(
      <AdaptiveNotification 
        notification={notification}
        onAction={handleAction}
        onClose={handleClose}
      />
    );

    expect(screen.getByText('Chat Session Ending Soon')).toBeInTheDocument();
    expect(screen.getByText('This chat session will terminate in 30 seconds.')).toBeInTheDocument();
    expect(screen.getByText('Extend Session')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Extend Session'));
    expect(handleAction).toHaveBeenCalledWith('notification-1', 'extendSession');

    fireEvent.click(screen.getByRole('button', { name: /close/i }));
    expect(handleClose).toHaveBeenCalledWith('notification-1');
  });

  test('NotificationProvider renders notifications from store', () => {
    render(
      <Provider store={store}>
        <NotificationProvider />
      </Provider>
    );

    expect(screen.getByText('Chat Session Ending Soon')).toBeInTheDocument();
    expect(screen.getByText('This chat session will terminate in 30 seconds.')).toBeInTheDocument();
  });

  test('AdaptiveLayout renders with correct structure', () => {
    const sidebarContent = <div data-testid="sidebar">Sidebar Content</div>;
    const toolbarContent = <div data-testid="toolbar">Toolbar Content</div>;
    const mainContent = <div data-testid="main">Main Content</div>;

    render(
      <Provider store={store}>
        <AdaptiveLayout
          title="Test Layout"
          sidebar={sidebarContent}
          toolbar={toolbarContent}
        >
          {mainContent}
        </AdaptiveLayout>
      </Provider>
    );

    expect(screen.getByText('Test Layout')).toBeInTheDocument();
    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('toolbar')).toBeInTheDocument();
    expect(screen.getByTestId('main')).toBeInTheDocument();
  });

  test('CaptchaBypassCollaboration renders correctly', async () => {
    // Mock WebSocket connection
    global.WebSocket = jest.fn().mockImplementation(() => ({
      send: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      close: jest.fn()
    }));

    render(
      <Provider store={store}>
        <CaptchaBypassCollaboration 
          userId="user-1"
          userName="John Doe"
        />
      </Provider>
    );

    expect(screen.getByText('CAPTCHA Assistance')).toBeInTheDocument();
    expect(screen.getByText('Upload CAPTCHA Image')).toBeInTheDocument();
    
    // Test file upload
    const file = new File(['dummy content'], 'captcha.png', { type: 'image/png' });
    const fileInput = screen.getByLabelText(/upload captcha image/i);
    
    Object.defineProperty(fileInput, 'files', {
      value: [file]
    });
    
    fireEvent.change(fileInput);
    
    await waitFor(() => {
      expect(screen.getByText('Analyzing CAPTCHA...')).toBeInTheDocument();
    });
  });

  test('CollaborationWorkspace renders session information', () => {
    render(
      <Provider store={store}>
        <CollaborationWorkspace 
          userId="user-1"
          userName="John Doe"
        />
      </Provider>
    );

    expect(screen.getByText('CAPTCHA Assistance')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Lumina AI')).toBeInTheDocument();
  });
});
