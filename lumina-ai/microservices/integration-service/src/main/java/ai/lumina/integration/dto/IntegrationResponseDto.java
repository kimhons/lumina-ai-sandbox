package ai.lumina.integration.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * Data Transfer Object for integration operation responses.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IntegrationResponseDto {
    
    private String requestId;
    private boolean success;
    private Map<String, Object> data;
    private String errorMessage;
    private String errorCode;
    private long executionTimeMs;
}
