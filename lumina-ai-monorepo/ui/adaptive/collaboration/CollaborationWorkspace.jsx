import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useSelector, useDispatch } from 'react-redux';
import { selectActiveSession, addAction } from './collaborationSlice';
import '../styles/CollaborationWorkspace.css';

/**
 * CollaborationWorkspace component for providing a shared workspace for real-time
 * collaboration between users and AI agents.
 */
const CollaborationWorkspace = ({ userId, userName }) => {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [socket, setSocket] = useState(null);
  
  const activeSession = useSelector(selectActiveSession);
  const dispatch = useDispatch();
  
  useEffect(() => {
    if (!activeSession) return;
    
    // Initialize WebSocket connection
    const ws = new WebSocket(`wss://${window.location.host}/api/collaboration/workspace`);
    
    ws.addEventListener('open', () => {
      ws.send(JSON.stringify({
        type: 'join',
        userId,
        userName,
        sessionId: activeSession.id
      }));
    });
    
    ws.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'action':
          dispatch(addAction({
            sessionId: activeSession.id,
            action: data.action
          }));
          break;
        case 'typing':
          setIsTyping(data.isTyping);
          break;
        default:
          console.log('Unknown message type:', data.type);
      }
    });
    
    setSocket(ws);
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [userId, userName, activeSession, dispatch]);
  
  const handleMessageChange = (event) => {
    setMessage(event.target.value);
    
    // Send typing indicator
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'typing',
        isTyping: event.target.value.length > 0,
        sessionId: activeSession?.id
      }));
    }
  };
  
  const handleSendMessage = (event) => {
    event.preventDefault();
    
    if (!message.trim()) return;
    
    // Send message action
    if (socket && socket.readyState === WebSocket.OPEN) {
      const action = {
        type: 'message',
        content: message,
        sender: {
          id: userId,
          name: userName
        }
      };
      
      socket.send(JSON.stringify({
        type: 'action',
        action,
        sessionId: activeSession?.id
      }));
      
      // Add action to local state
      dispatch(addAction({
        sessionId: activeSession.id,
        action
      }));
      
      // Clear message input
      setMessage('');
      
      // Clear typing indicator
      socket.send(JSON.stringify({
        type: 'typing',
        isTyping: false,
        sessionId: activeSession?.id
      }));
    }
  };
  
  if (!activeSession) {
    return (
      <div className="collaboration-workspace-empty">
        <p>No active collaboration session.</p>
      </div>
    );
  }
  
  return (
    <div className="collaboration-workspace">
      <div className="collaboration-workspace-header">
        <h2>{activeSession.title}</h2>
        <div className="collaboration-participants">
          {activeSession.participants.map(participant => (
            <div key={participant.id} className={`participant ${participant.role}`}>
              {participant.name}
            </div>
          ))}
        </div>
      </div>
      
      <div className="collaboration-workspace-content">
        <div className="collaboration-actions">
          {activeSession.actions.map((action, index) => (
            <div 
              key={index} 
              className={`collaboration-action ${action.type} ${
                action.sender.id === userId ? 'self' : 'other'
              }`}
            >
              <div className="action-sender">{action.sender.name}</div>
              <div className="action-content">
                {action.type === 'message' ? (
                  <div className="action-message">{action.content}</div>
                ) : action.type === 'file' ? (
                  <div className="action-file">
                    <a href={action.url} target="_blank" rel="noopener noreferrer">
                      {action.filename}
                    </a>
                  </div>
                ) : action.type === 'annotation' ? (
                  <div className="action-annotation">
                    <div className="annotation-target">{action.target}</div>
                    <div className="annotation-text">{action.text}</div>
                  </div>
                ) : (
                  <div className="action-unknown">Unknown action type</div>
                )}
              </div>
              <div className="action-timestamp">
                {new Date(action.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))}
        </div>
        
        <div className="collaboration-input">
          {isTyping && (
            <div className="typing-indicator">
              Agent is typing...
            </div>
          )}
          
          <form onSubmit={handleSendMessage} className="message-form">
            <input
              type="text"
              value={message}
              onChange={handleMessageChange}
              placeholder="Type a message..."
              className="message-input"
            />
            <button 
              type="submit" 
              className="send-button"
              disabled={!message.trim()}
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

CollaborationWorkspace.propTypes = {
  userId: PropTypes.string.isRequired,
  userName: PropTypes.string.isRequired
};

export default CollaborationWorkspace;
