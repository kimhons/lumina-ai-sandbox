package ai.lumina.ui.adaptive.websocket;

import org.springframework.stereotype.Controller;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.messaging.simp.SimpMessageHeaderAccessor;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.beans.factory.annotation.Autowired;

import ai.lumina.ui.adaptive.model.CollaborationSession;
import ai.lumina.ui.adaptive.service.AdaptiveUIService;

import java.util.Map;
import java.util.HashMap;

/**
 * WebSocket controller for real-time collaboration features in the Adaptive UI system.
 */
@Controller
public class CollaborationWebSocketController {

    @Autowired
    private SimpMessagingTemplate messagingTemplate;
    
    @Autowired
    private AdaptiveUIService adaptiveUIService;
    
    /**
     * Handle joining a collaboration session
     */
    @MessageMapping("/collaboration/join")
    public void joinSession(@Payload Map<String, Object> payload, SimpMessageHeaderAccessor headerAccessor) {
        String sessionId = (String) payload.get("sessionId");
        String userId = (String) payload.get("userId");
        String userName = (String) payload.get("userName");
        
        // Store session ID in WebSocket session
        headerAccessor.getSessionAttributes().put("sessionId", sessionId);
        headerAccessor.getSessionAttributes().put("userId", userId);
        
        // Get the collaboration session
        CollaborationSession session = adaptiveUIService.getCollaborationSession(sessionId);
        
        if (session != null) {
            // Create join message
            Map<String, Object> message = new HashMap<>();
            message.put("type", "JOIN");
            message.put("sessionId", sessionId);
            message.put("userId", userId);
            message.put("userName", userName);
            message.put("timestamp", System.currentTimeMillis());
            
            // Broadcast to all session participants
            messagingTemplate.convertAndSend("/topic/collaboration/" + sessionId, message);
        }
    }
    
    /**
     * Handle collaboration actions
     */
    @MessageMapping("/collaboration/action")
    @SendTo("/topic/collaboration/{sessionId}")
    public Map<String, Object> processAction(@Payload Map<String, Object> payload) {
        String sessionId = (String) payload.get("sessionId");
        String userId = (String) payload.get("userId");
        String actionType = (String) payload.get("actionType");
        String content = (String) payload.get("content");
        
        // Create action
        CollaborationSession.CollaborationAction action = new CollaborationSession.CollaborationAction();
        action.setParticipantId(userId);
        action.setType(actionType);
        action.setContent(content);
        
        // Add action to session
        CollaborationSession session = adaptiveUIService.addCollaborationAction(sessionId, action);
        
        // Create response
        Map<String, Object> response = new HashMap<>();
        response.put("type", "ACTION");
        response.put("sessionId", sessionId);
        response.put("userId", userId);
        response.put("actionId", action.getId());
        response.put("actionType", actionType);
        response.put("content", content);
        response.put("timestamp", action.getTimestamp().getTime());
        response.put("status", action.getStatus());
        
        return response;
    }
    
    /**
     * Handle CAPTCHA assistance requests
     */
    @MessageMapping("/collaboration/captcha")
    public void processCaptchaRequest(@Payload Map<String, Object> payload) {
        String sessionId = (String) payload.get("sessionId");
        String userId = (String) payload.get("userId");
        String captchaType = (String) payload.get("captchaType");
        String imageData = (String) payload.get("imageData");
        
        // In a real implementation, this would process the CAPTCHA image
        // and provide assistance through the AI agent
        
        // For now, just send a response with guidance
        Map<String, Object> response = new HashMap<>();
        response.put("type", "CAPTCHA_GUIDANCE");
        response.put("sessionId", sessionId);
        response.put("userId", "agent"); // From the AI agent
        response.put("captchaType", captchaType);
        response.put("guidance", "I can see this is a text-based CAPTCHA. The characters appear to be: " + generateSampleGuidance(captchaType));
        response.put("confidence", 0.85);
        response.put("timestamp", System.currentTimeMillis());
        
        // Send to the specific user
        messagingTemplate.convertAndSendToUser(userId, "/queue/collaboration/" + sessionId, response);
    }
    
    /**
     * Generate sample guidance for demonstration purposes
     */
    private String generateSampleGuidance(String captchaType) {
        if ("text".equals(captchaType)) {
            return "X7R9P2";
        } else if ("image".equals(captchaType)) {
            return "Please select all images containing traffic lights";
        } else {
            return "Please follow the instructions on the CAPTCHA";
        }
    }
}
