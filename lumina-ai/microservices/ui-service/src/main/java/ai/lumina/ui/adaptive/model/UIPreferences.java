package ai.lumina.ui.adaptive.model;

import java.util.Map;
import java.util.HashMap;
import java.util.Date;
import java.io.Serializable;

/**
 * Model class representing user UI preferences.
 * Contains all customizable aspects of the Adaptive UI system.
 */
public class UIPreferences implements Serializable {
    private String userId;
    private Map<String, Object> appearance;
    private Map<String, Object> behavior;
    private Map<String, Object> accessibility;
    private Map<String, Object> notifications;
    private Map<String, Object> privacy;
    private Date lastUpdated;

    public UIPreferences() {
        // Initialize with default values
        this.appearance = new HashMap<>();
        this.behavior = new HashMap<>();
        this.accessibility = new HashMap<>();
        this.notifications = new HashMap<>();
        this.privacy = new HashMap<>();
        this.lastUpdated = new Date();
        
        initializeDefaults();
    }

    public UIPreferences(String userId) {
        this();
        this.userId = userId;
    }

    private void initializeDefaults() {
        // Appearance defaults
        appearance.put("theme", "light");
        appearance.put("fontSize", "medium");
        appearance.put("accentColor", "#007AFF");
        appearance.put("messageGrouping", true);
        appearance.put("showTimestamps", true);
        
        // Behavior defaults
        behavior.put("autoScrollEnabled", true);
        behavior.put("soundEnabled", true);
        behavior.put("typingIndicators", true);
        behavior.put("sendOnEnter", true);
        behavior.put("autoSuggest", true);
        
        // Accessibility defaults
        accessibility.put("highContrast", false);
        accessibility.put("reducedMotion", false);
        accessibility.put("screenReaderOptimized", false);
        accessibility.put("keyboardNavigation", true);
        accessibility.put("textToSpeech", false);
        
        // Notification defaults
        notifications.put("chatTermination", true);
        notifications.put("newMessages", true);
        notifications.put("collaborationInvites", true);
        notifications.put("systemUpdates", false);
        notifications.put("notificationSound", "subtle");
        
        // Privacy defaults
        privacy.put("saveHistory", true);
        privacy.put("shareAnalytics", false);
        privacy.put("personalizedSuggestions", true);
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public Map<String, Object> getAppearance() {
        return appearance;
    }

    public void setAppearance(Map<String, Object> appearance) {
        this.appearance = appearance;
        this.lastUpdated = new Date();
    }

    public Map<String, Object> getBehavior() {
        return behavior;
    }

    public void setBehavior(Map<String, Object> behavior) {
        this.behavior = behavior;
        this.lastUpdated = new Date();
    }

    public Map<String, Object> getAccessibility() {
        return accessibility;
    }

    public void setAccessibility(Map<String, Object> accessibility) {
        this.accessibility = accessibility;
        this.lastUpdated = new Date();
    }

    public Map<String, Object> getNotifications() {
        return notifications;
    }

    public void setNotifications(Map<String, Object> notifications) {
        this.notifications = notifications;
        this.lastUpdated = new Date();
    }

    public Map<String, Object> getPrivacy() {
        return privacy;
    }

    public void setPrivacy(Map<String, Object> privacy) {
        this.privacy = privacy;
        this.lastUpdated = new Date();
    }

    public Date getLastUpdated() {
        return lastUpdated;
    }

    public void setLastUpdated(Date lastUpdated) {
        this.lastUpdated = lastUpdated;
    }

    /**
     * Update a specific preference category
     * @param category The category to update
     * @param values The new values
     * @return true if the update was successful
     */
    public boolean updateCategory(String category, Map<String, Object> values) {
        switch (category) {
            case "appearance":
                appearance.putAll(values);
                break;
            case "behavior":
                behavior.putAll(values);
                break;
            case "accessibility":
                accessibility.putAll(values);
                break;
            case "notifications":
                notifications.putAll(values);
                break;
            case "privacy":
                privacy.putAll(values);
                break;
            default:
                return false;
        }
        
        this.lastUpdated = new Date();
        return true;
    }

    /**
     * Update a specific preference setting
     * @param category The category containing the setting
     * @param setting The setting name
     * @param value The new value
     * @return true if the update was successful
     */
    public boolean updateSetting(String category, String setting, Object value) {
        Map<String, Object> categoryMap = null;
        
        switch (category) {
            case "appearance":
                categoryMap = appearance;
                break;
            case "behavior":
                categoryMap = behavior;
                break;
            case "accessibility":
                categoryMap = accessibility;
                break;
            case "notifications":
                categoryMap = notifications;
                break;
            case "privacy":
                categoryMap = privacy;
                break;
            default:
                return false;
        }
        
        if (categoryMap != null) {
            categoryMap.put(setting, value);
            this.lastUpdated = new Date();
            return true;
        }
        
        return false;
    }

    /**
     * Get all preferences as a single map
     * @return Map containing all preference categories
     */
    public Map<String, Object> toMap() {
        Map<String, Object> allPreferences = new HashMap<>();
        allPreferences.put("userId", userId);
        allPreferences.put("appearance", appearance);
        allPreferences.put("behavior", behavior);
        allPreferences.put("accessibility", accessibility);
        allPreferences.put("notifications", notifications);
        allPreferences.put("privacy", privacy);
        allPreferences.put("lastUpdated", lastUpdated);
        return allPreferences;
    }
}
