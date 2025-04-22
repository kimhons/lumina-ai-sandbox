package ai.lumina.ui.adaptive.model;

import java.util.Date;
import java.util.UUID;
import java.io.Serializable;

/**
 * Model class representing a notification in the Adaptive UI system.
 */
public class Notification implements Serializable {
    private String id;
    private String userId;
    private String type;
    private String title;
    private String message;
    private boolean closable;
    private String action;
    private String actionText;
    private long duration;
    private Date createdAt;
    private boolean read;
    private String sessionId;

    public Notification() {
        this.id = UUID.randomUUID().toString();
        this.createdAt = new Date();
        this.closable = true;
        this.read = false;
        this.duration = 5000; // Default duration: 5 seconds
        this.type = "default";
    }

    public Notification(String userId, String type, String title, String message) {
        this();
        this.userId = userId;
        this.type = type;
        this.title = title;
        this.message = message;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public boolean isClosable() {
        return closable;
    }

    public void setClosable(boolean closable) {
        this.closable = closable;
    }

    public String getAction() {
        return action;
    }

    public void setAction(String action) {
        this.action = action;
    }

    public String getActionText() {
        return actionText;
    }

    public void setActionText(String actionText) {
        this.actionText = actionText;
    }

    public long getDuration() {
        return duration;
    }

    public void setDuration(long duration) {
        this.duration = duration;
    }

    public Date getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Date createdAt) {
        this.createdAt = createdAt;
    }

    public boolean isRead() {
        return read;
    }

    public void setRead(boolean read) {
        this.read = read;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    /**
     * Create a chat termination warning notification
     * @param userId The user ID
     * @param sessionId The chat session ID
     * @param timeRemaining Time remaining in seconds
     * @return A new notification
     */
    public static Notification createChatTerminationWarning(String userId, String sessionId, int timeRemaining) {
        Notification notification = new Notification();
        notification.setUserId(userId);
        notification.setType("warning");
        notification.setTitle("Chat Session Ending Soon");
        notification.setMessage("This chat session will terminate in " + timeRemaining + " seconds.");
        notification.setDuration(0); // Don't auto-dismiss
        notification.setAction("extendSession");
        notification.setActionText("Extend Session");
        notification.setSessionId(sessionId);
        notification.setClosable(true);
        return notification;
    }

    /**
     * Create a success notification
     * @param userId The user ID
     * @param title The notification title
     * @param message The notification message
     * @return A new notification
     */
    public static Notification createSuccessNotification(String userId, String title, String message) {
        Notification notification = new Notification();
        notification.setUserId(userId);
        notification.setType("success");
        notification.setTitle(title);
        notification.setMessage(message);
        return notification;
    }

    /**
     * Create an error notification
     * @param userId The user ID
     * @param title The notification title
     * @param message The notification message
     * @return A new notification
     */
    public static Notification createErrorNotification(String userId, String title, String message) {
        Notification notification = new Notification();
        notification.setUserId(userId);
        notification.setType("error");
        notification.setTitle(title);
        notification.setMessage(message);
        return notification;
    }

    /**
     * Create a warning notification
     * @param userId The user ID
     * @param title The notification title
     * @param message The notification message
     * @return A new notification
     */
    public static Notification createWarningNotification(String userId, String title, String message) {
        Notification notification = new Notification();
        notification.setUserId(userId);
        notification.setType("warning");
        notification.setTitle(title);
        notification.setMessage(message);
        return notification;
    }

    /**
     * Create an info notification
     * @param userId The user ID
     * @param title The notification title
     * @param message The notification message
     * @return A new notification
     */
    public static Notification createInfoNotification(String userId, String title, String message) {
        Notification notification = new Notification();
        notification.setUserId(userId);
        notification.setType("info");
        notification.setTitle(title);
        notification.setMessage(message);
        return notification;
    }
}
