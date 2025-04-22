package ai.lumina.ui.adaptive.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * Data Transfer Object for UI Preferences
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UIPreferencesDto {
    
    private Long id;
    private String userId;
    private String theme;
    private String language;
    private String timezone;
    private Boolean notificationsEnabled;
    private Boolean soundEnabled;
    private Integer fontSize;
    private Boolean highContrastMode;
    private Boolean reducedMotion;
    private Map<String, Object> additionalPreferences;
    private LocalDateTime lastUpdated;
}
