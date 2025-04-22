package ai.lumina.ui.adaptive.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Data Transfer Object for Notifications
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class NotificationDto {
    
    private Long id;
    private String userId;
    private String title;
    private String message;
    private String type;
    private Boolean read;
    private Integer priority;
    private Integer timeoutMs;
    private Boolean dismissible;
    private String actionUrl;
    private String actionText;
    private LocalDateTime createdAt;
    private LocalDateTime expiresAt;
}
