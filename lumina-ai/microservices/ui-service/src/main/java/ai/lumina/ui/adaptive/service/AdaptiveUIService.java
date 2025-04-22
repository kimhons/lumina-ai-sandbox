package ai.lumina.ui.adaptive.service;

import ai.lumina.ui.adaptive.model.UIPreferences;
import ai.lumina.ui.adaptive.model.Notification;
import ai.lumina.ui.adaptive.model.CollaborationSession;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * Service for managing UI preferences in the Adaptive UI system.
 */
@Service
public class AdaptiveUIService {
    
    // In-memory storage for preferences (would be replaced with database in production)
    private final Map<String, UIPreferences> preferencesStore = new ConcurrentHashMap<>();
    
    // In-memory storage for notifications
    private final Map<String, List<Notification>> notificationsStore = new ConcurrentHashMap<>();
    
    // In-memory storage for collaboration sessions
    private final Map<String, CollaborationSession> collaborationSessionsStore = new ConcurrentHashMap<>();
    
    /**
     * Get UI preferences for a user
     * @param userId The user ID
     * @return The user's UI preferences
     */
    public UIPreferences getUserPreferences(String userId) {
        return preferencesStore.computeIfAbsent(userId, UIPreferences::new);
    }
    
    /**
     * Update UI preferences for a user
     * @param userId The user ID
     * @param preferences The updated preferences
     * @return The updated preferences
     */
    public UIPreferences updateUserPreferences(String userId, UIPreferences preferences) {
        preferences.setUserId(userId);
        preferencesStore.put(userId, preferences);
        return preferences;
    }
    
    /**
     * Update a specific preference category for a user
     * @param userId The user ID
     * @param category The category to update
     * @param values The new values
     * @return The updated preferences
     */
    public UIPreferences updatePreferenceCategory(String userId, String category, Map<String, Object> values) {
        UIPreferences preferences = getUserPreferences(userId);
        preferences.updateCategory(category, values);
        return preferences;
    }
    
    /**
     * Update a specific preference setting for a user
     * @param userId The user ID
     * @param category The category containing the setting
     * @param setting The setting name
     * @param value The new value
     * @return The updated preferences
     */
    public UIPreferences updatePreferenceSetting(String userId, String category, String setting, Object value) {
        UIPreferences preferences = getUserPreferences(userId);
        preferences.updateSetting(category, setting, value);
        return preferences;
    }
    
    /**
     * Get all notifications for a user
     * @param userId The user ID
     * @return List of notifications
     */
    public List<Notification> getUserNotifications(String userId) {
        return notificationsStore.getOrDefault(userId, new ArrayList<>());
    }
    
    /**
     * Add a notification for a user
     * @param notification The notification to add
     * @return The added notification
     */
    public Notification addNotification(Notification notification) {
        String userId = notification.getUserId();
        List<Notification> notifications = notificationsStore.computeIfAbsent(userId, k -> new ArrayList<>());
        notifications.add(notification);
        return notification;
    }
    
    /**
     * Remove a notification
     * @param userId The user ID
     * @param notificationId The notification ID
     * @return true if the notification was removed
     */
    public boolean removeNotification(String userId, String notificationId) {
        List<Notification> notifications = notificationsStore.get(userId);
        if (notifications == null) {
            return false;
        }
        
        int initialSize = notifications.size();
        notifications.removeIf(n -> n.getId().equals(notificationId));
        return notifications.size() < initialSize;
    }
    
    /**
     * Create a chat termination warning notification
     * @param userId The user ID
     * @param sessionId The chat session ID
     * @param timeRemaining Time remaining in seconds
     * @return The created notification
     */
    public Notification createChatTerminationWarning(String userId, String sessionId, int timeRemaining) {
        Notification notification = Notification.createChatTerminationWarning(userId, sessionId, timeRemaining);
        return addNotification(notification);
    }
    
    /**
     * Get a collaboration session
     * @param sessionId The session ID
     * @return The collaboration session
     */
    public CollaborationSession getCollaborationSession(String sessionId) {
        return collaborationSessionsStore.get(sessionId);
    }
    
    /**
     * Create a new collaboration session
     * @param session The session to create
     * @return The created session
     */
    public CollaborationSession createCollaborationSession(CollaborationSession session) {
        collaborationSessionsStore.put(session.getId(), session);
        return session;
    }
    
    /**
     * Create a CAPTCHA bypass collaboration session
     * @param userId The user ID
     * @param userName The user name
     * @param agentId The agent ID
     * @param agentName The agent name
     * @return The created session
     */
    public CollaborationSession createCaptchaBypassSession(String userId, String userName, String agentId, String agentName) {
        CollaborationSession session = CollaborationSession.createCaptchaBypassSession(userId, userName, agentId, agentName);
        return createCollaborationSession(session);
    }
    
    /**
     * Add an action to a collaboration session
     * @param sessionId The session ID
     * @param action The action to add
     * @return The updated session
     */
    public CollaborationSession addCollaborationAction(String sessionId, CollaborationSession.CollaborationAction action) {
        CollaborationSession session = getCollaborationSession(sessionId);
        if (session != null) {
            session.addAction(action);
        }
        return session;
    }
}
