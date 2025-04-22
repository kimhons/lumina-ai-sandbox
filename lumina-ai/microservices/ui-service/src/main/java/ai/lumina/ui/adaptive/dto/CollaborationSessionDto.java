package ai.lumina.ui.adaptive.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * Data Transfer Object for Collaboration Sessions
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CollaborationSessionDto {
    
    private Long id;
    private String sessionId;
    private String sessionType;
    private String title;
    private String description;
    private List<String> participants;
    private String createdBy;
    private Boolean active;
    private Map<String, Object> sessionData;
    private LocalDateTime createdAt;
    private LocalDateTime lastActivity;
    private LocalDateTime expiresAt;
}
