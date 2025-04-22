package ai.lumina.integration.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * Data Transfer Object for integration operation requests.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IntegrationRequestDto {
    
    private String systemId;
    private String operation;
    private Map<String, Object> params;
    private Map<String, Object> context;
}
