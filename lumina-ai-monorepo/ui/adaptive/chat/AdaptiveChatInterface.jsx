import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useSelector, useDispatch } from 'react-redux';
import '../styles/AdaptiveChatInterface.css';

/**
 * AdaptiveChatInterface component for providing an adaptive chat experience
 * with features like chat termination notifications and real-time collaboration.
 */
const AdaptiveChatInterface = ({ userId, userName }) => {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionInfo, setSessionInfo] = useState(null);
  
  const preferences = useSelector(state => state.preferences);
  const dispatch = useDispatch();
  
  useEffect(() => {
    // Initialize chat session
    fetch(`/api/chat/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        userId,
        userName
      })
    })
    .then(response => response.json())
    .then(data => {
      setSessionInfo(data);
      
      // Set up session timeout warning
      if (data.expiresAt) {
        const expiresAt = new Date(data.expiresAt).getTime();
        const warningTime = 30000; // 30 seconds before expiration
        
        const timeUntilWarning = expiresAt - Date.now() - warningTime;
        
        if (timeUntilWarning > 0) {
          setTimeout(() => {
            dispatch({
              type: 'notifications/showChatTerminationWarning',
              payload: {
                timeRemaining: 30,
                sessionId: data.id
              }
            });
          }, timeUntilWarning);
        }
      }
    })
    .catch(error => {
      console.error('Error initializing chat session:', error);
    });
    
    // Clean up on unmount
    return () => {
      if (sessionInfo) {
        fetch(`/api/chat/sessions/${sessionInfo.id}`, {
          method: 'DELETE'
        }).catch(error => {
          console.error('Error closing chat session:', error);
        });
      }
    };
  }, [userId, userName, dispatch]);
  
  const handleSendMessage = (event) => {
    event.preventDefault();
    
    if (!message.trim() || !sessionInfo) return;
    
    // Add user message to chat history
    const userMessage = {
      id: `msg-${Date.now()}`,
      content: message,
      sender: {
        id: userId,
        name: userName,
        type: 'user'
      },
      timestamp: new Date().toISOString()
    };
    
    setChatHistory(prevHistory => [...prevHistory, userMessage]);
    setMessage('');
    setIsTyping(true);
    
    // Send message to API
    fetch(`/api/chat/sessions/${sessionInfo.id}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: message
      })
    })
    .then(response => response.json())
    .then(data => {
      setIsTyping(false);
      
      // Add AI response to chat history
      const aiMessage = {
        id: data.id,
        content: data.content,
        sender: {
          id: data.sender.id,
          name: data.sender.name,
          type: 'ai'
        },
        timestamp: data.timestamp
      };
      
      setChatHistory(prevHistory => [...prevHistory, aiMessage]);
    })
    .catch(error => {
      setIsTyping(false);
      console.error('Error sending message:', error);
    });
  };
  
  const handleMessageChange = (event) => {
    setMessage(event.target.value);
  };
  
  const renderChatMessage = (message) => {
    const isUser = message.sender.type === 'user';
    
    return (
      <div 
        key={message.id} 
        className={`chat-message ${isUser ? 'user-message' : 'ai-message'}`}
      >
        <div className="message-sender">{message.sender.name}</div>
        <div className="message-content">{message.content}</div>
        <div className="message-timestamp">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    );
  };
  
  return (
    <div className={`adaptive-chat-interface theme-${preferences.appearance.theme}`}>
      <div className="chat-header">
        <h2>Chat Session</h2>
        {sessionInfo && (
          <div className="session-info">
            <span className="session-id">ID: {sessionInfo.id}</span>
            {sessionInfo.expiresAt && (
              <span className="session-expiry">
                Expires: {new Date(sessionInfo.expiresAt).toLocaleTimeString()}
              </span>
            )}
          </div>
        )}
      </div>
      
      <div className="chat-messages">
        {chatHistory.map(renderChatMessage)}
        
        {isTyping && (
          <div className="typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        )}
      </div>
      
      <form onSubmit={handleSendMessage} className="chat-input-form">
        <input
          type="text"
          value={message}
          onChange={handleMessageChange}
          placeholder="Type your message..."
          className="chat-input"
          style={{ fontSize: preferences.appearance.fontSize }}
        />
        <button 
          type="submit" 
          className="chat-send-button"
          disabled={!message.trim() || !sessionInfo}
        >
          Send
        </button>
      </form>
    </div>
  );
};

AdaptiveChatInterface.propTypes = {
  userId: PropTypes.string.isRequired,
  userName: PropTypes.string.isRequired
};

export default AdaptiveChatInterface;
