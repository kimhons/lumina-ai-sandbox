package ai.lumina.ui.adaptive.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Data Transfer Object for Chat Termination Notification
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatTerminationDto {
    
    private String sessionId;
    private String userId;
    private Integer timeoutSeconds;
    private Boolean canExtend;
    private Integer maxExtensionMinutes;
    private String terminationReason;
}
