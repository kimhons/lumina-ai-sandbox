package ai.lumina.integration.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Data Transfer Object for EnterpriseSystem.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EnterpriseSystemDto {
    
    private String systemId;
    private String systemType;
    private String name;
    private String description;
    private boolean enabled;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Map<String, String> connectionParams = new HashMap<>();
    private Map<String, String> authParams = new HashMap<>();
    private Map<String, String> transformParams = new HashMap<>();
    private Map<String, String> metadata = new HashMap<>();
}
