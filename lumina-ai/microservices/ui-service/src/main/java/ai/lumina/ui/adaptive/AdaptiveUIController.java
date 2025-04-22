package ai.lumina.ui.adaptive;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.PathVariable;

import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;
import java.util.UUID;

/**
 * Controller for the Adaptive UI system.
 * Provides endpoints for managing UI preferences, notifications, and chat sessions.
 */
@Controller
@RequestMapping("/api/ui/adaptive")
public class AdaptiveUIController {

    /**
     * Get the current UI preferences for a user
     */
    @GetMapping("/preferences/{userId}")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> getUserPreferences(@PathVariable String userId) {
        // In a real implementation, this would fetch from a database
        Map<String, Object> preferences = new HashMap<>();
        
        // Appearance preferences
        Map<String, Object> appearance = new HashMap<>();
        appearance.put("theme", "light");
        appearance.put("fontSize", "medium");
        appearance.put("accentColor", "#007AFF");
        appearance.put("messageGrouping", true);
        appearance.put("showTimestamps", true);
        preferences.put("appearance", appearance);
        
        // Behavior preferences
        Map<String, Object> behavior = new HashMap<>();
        behavior.put("autoScrollEnabled", true);
        behavior.put("soundEnabled", true);
        behavior.put("typingIndicators", true);
        behavior.put("sendOnEnter", true);
        behavior.put("autoSuggest", true);
        preferences.put("behavior", behavior);
        
        // Accessibility preferences
        Map<String, Object> accessibility = new HashMap<>();
        accessibility.put("highContrast", false);
        accessibility.put("reducedMotion", false);
        accessibility.put("screenReaderOptimized", false);
        accessibility.put("keyboardNavigation", true);
        accessibility.put("textToSpeech", false);
        preferences.put("accessibility", accessibility);
        
        // Notification preferences
        Map<String, Object> notifications = new HashMap<>();
        notifications.put("chatTermination", true);
        notifications.put("newMessages", true);
        notifications.put("collaborationInvites", true);
        notifications.put("systemUpdates", false);
        notifications.put("notificationSound", "subtle");
        preferences.put("notifications", notifications);
        
        // Privacy preferences
        Map<String, Object> privacy = new HashMap<>();
        privacy.put("saveHistory", true);
        privacy.put("shareAnalytics", false);
        privacy.put("personalizedSuggestions", true);
        preferences.put("privacy", privacy);
        
        return ResponseEntity.ok(preferences);
    }
    
    /**
     * Update UI preferences for a user
     */
    @PostMapping("/preferences/{userId}")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> updateUserPreferences(
            @PathVariable String userId,
            @RequestBody Map<String, Object> preferences) {
        
        // In a real implementation, this would update a database
        // For now, just return the updated preferences
        Map<String, Object> response = new HashMap<>();
        response.put("userId", userId);
        response.put("preferences", preferences);
        response.put("updated", true);
        
        return ResponseEntity.ok(response);
    }
    
    /**
     * Get active notifications for a user
     */
    @GetMapping("/notifications/{userId}")
    @ResponseBody
    public ResponseEntity<List<Map<String, Object>>> getUserNotifications(@PathVariable String userId) {
        // In a real implementation, this would fetch from a database
        List<Map<String, Object>> notifications = new ArrayList<>();
        
        // Example notification
        Map<String, Object> notification = new HashMap<>();
        notification.put("id", UUID.randomUUID().toString());
        notification.put("type", "info");
        notification.put("title", "Welcome to Lumina AI");
        notification.put("message", "Explore the new Adaptive UI features");
        notification.put("createdAt", System.currentTimeMillis());
        notifications.add(notification);
        
        return ResponseEntity.ok(notifications);
    }
    
    /**
     * Create a new notification for a user
     */
    @PostMapping("/notifications/{userId}")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> createNotification(
            @PathVariable String userId,
            @RequestBody Map<String, Object> notification) {
        
        // In a real implementation, this would store in a database
        // For now, just return the created notification with an ID
        String notificationId = UUID.randomUUID().toString();
        Map<String, Object> response = new HashMap<>(notification);
        response.put("id", notificationId);
        response.put("createdAt", System.currentTimeMillis());
        
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
    
    /**
     * Get chat session information
     */
    @GetMapping("/chat/sessions/{sessionId}")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> getChatSession(@PathVariable String sessionId) {
        // In a real implementation, this would fetch from a database
        Map<String, Object> session = new HashMap<>();
        session.put("id", sessionId);
        session.put("title", "Chat Session");
        session.put("createdAt", System.currentTimeMillis() - 3600000); // 1 hour ago
        session.put("lastActivity", System.currentTimeMillis() - 60000); // 1 minute ago
        session.put("status", "active");
        
        // Session timeout information
        Map<String, Object> timeout = new HashMap<>();
        timeout.put("expiresAt", System.currentTimeMillis() + 1800000); // 30 minutes from now
        timeout.put("warningShown", false);
        timeout.put("extended", false);
        session.put("timeout", timeout);
        
        return ResponseEntity.ok(session);
    }
    
    /**
     * Extend a chat session
     */
    @PostMapping("/chat/sessions/{sessionId}/extend")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> extendChatSession(
            @PathVariable String sessionId,
            @RequestBody Map<String, Object> request) {
        
        // Get extension minutes from request, default to 30
        int extensionMinutes = 30;
        if (request.containsKey("extensionMinutes")) {
            extensionMinutes = (Integer) request.get("extensionMinutes");
        }
        
        // In a real implementation, this would update a database
        Map<String, Object> response = new HashMap<>();
        response.put("sessionId", sessionId);
        response.put("extended", true);
        response.put("extensionMinutes", extensionMinutes);
        response.put("newExpiryTime", System.currentTimeMillis() + (extensionMinutes * 60 * 1000));
        
        return ResponseEntity.ok(response);
    }
    
    /**
     * Get collaboration session information
     */
    @GetMapping("/collaboration/sessions/{sessionId}")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> getCollaborationSession(@PathVariable String sessionId) {
        // In a real implementation, this would fetch from a database
        Map<String, Object> session = new HashMap<>();
        session.put("id", sessionId);
        session.put("title", "Collaboration Session");
        session.put("type", "captcha-bypass"); // or "general"
        session.put("createdAt", System.currentTimeMillis() - 1800000); // 30 minutes ago
        session.put("status", "active");
        
        // Participants
        List<Map<String, Object>> participants = new ArrayList<>();
        Map<String, Object> user = new HashMap<>();
        user.put("id", "user-123");
        user.put("name", "John Doe");
        user.put("role", "user");
        participants.add(user);
        
        Map<String, Object> agent = new HashMap<>();
        agent.put("id", "agent-456");
        agent.put("name", "Lumina AI");
        agent.put("role", "agent");
        participants.add(agent);
        
        session.put("participants", participants);
        
        return ResponseEntity.ok(session);
    }
}
