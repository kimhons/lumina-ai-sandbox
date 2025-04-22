import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useSelector, useDispatch } from 'react-redux';
import '../styles/CaptchaBypassCollaboration.css';

/**
 * CaptchaBypassCollaboration component for real-time collaboration between user and AI agent
 * to solve CAPTCHA challenges.
 */
const CaptchaBypassCollaboration = ({ userId, userName }) => {
  const [captchaImage, setCaptchaImage] = useState(null);
  const [captchaText, setCaptchaText] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [guidance, setGuidance] = useState('');
  const [socket, setSocket] = useState(null);
  
  const session = useSelector(state => {
    const sessions = state.collaboration.sessions;
    const activeSessionId = state.collaboration.activeSessionId;
    return sessions[activeSessionId];
  });
  
  const dispatch = useDispatch();
  
  useEffect(() => {
    // Initialize WebSocket connection
    const ws = new WebSocket(`wss://${window.location.host}/api/collaboration/captcha`);
    
    ws.addEventListener('open', () => {
      ws.send(JSON.stringify({
        type: 'join',
        userId,
        userName,
        sessionId: session?.id
      }));
    });
    
    ws.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'analysis':
          setAnalyzing(false);
          setGuidance(data.guidance);
          break;
        case 'suggestion':
          setCaptchaText(data.text);
          break;
        case 'success':
          // Handle successful CAPTCHA solution
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
  }, [userId, userName, session]);
  
  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      const imageData = e.target.result;
      setCaptchaImage(imageData);
      setAnalyzing(true);
      setGuidance('');
      
      // Send image to server for analysis
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          type: 'analyze',
          image: imageData,
          sessionId: session?.id
        }));
      }
    };
    reader.readAsDataURL(file);
  };
  
  const handleTextChange = (event) => {
    setCaptchaText(event.target.value);
    
    // Send text update to server
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'text_update',
        text: event.target.value,
        sessionId: session?.id
      }));
    }
  };
  
  const handleSubmit = (event) => {
    event.preventDefault();
    
    // Send submission to server
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'submit',
        text: captchaText,
        sessionId: session?.id
      }));
    }
  };
  
  return (
    <div className="captcha-bypass-container">
      <h2 className="captcha-bypass-title">{session?.title || 'CAPTCHA Assistance'}</h2>
      
      <div className="captcha-bypass-content">
        <div className="captcha-image-section">
          <label htmlFor="captcha-image-upload" className="captcha-image-upload-label">
            Upload CAPTCHA Image
            <input
              id="captcha-image-upload"
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="captcha-image-upload-input"
            />
          </label>
          
          {captchaImage && (
            <div className="captcha-image-preview">
              <img src={captchaImage} alt="CAPTCHA" className="captcha-image" />
            </div>
          )}
        </div>
        
        <div className="captcha-solution-section">
          {analyzing ? (
            <div className="captcha-analyzing">
              <div className="captcha-analyzing-spinner"></div>
              <p>Analyzing CAPTCHA...</p>
            </div>
          ) : (
            guidance && (
              <div className="captcha-guidance">
                <h3>AI Guidance:</h3>
                <p>{guidance}</p>
              </div>
            )
          )}
          
          <form onSubmit={handleSubmit} className="captcha-form">
            <div className="captcha-input-group">
              <label htmlFor="captcha-text">CAPTCHA Solution:</label>
              <input
                id="captcha-text"
                type="text"
                value={captchaText}
                onChange={handleTextChange}
                placeholder="Enter CAPTCHA text"
                className="captcha-text-input"
              />
            </div>
            
            <button 
              type="submit" 
              className="captcha-submit-button"
              disabled={!captchaText || analyzing}
            >
              Submit Solution
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

CaptchaBypassCollaboration.propTypes = {
  userId: PropTypes.string.isRequired,
  userName: PropTypes.string.isRequired
};

export default CaptchaBypassCollaboration;
