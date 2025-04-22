package ai.lumina.ui.adaptive.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * Data Transfer Object for Collaboration Messages
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CollaborationMessageDto {
    
    private String sessionId;
    private String senderId;
    private String senderName;
    private String messageType;
    private String content;
    private Map<String, Object> metadata;
    private Long timestamp;
}
