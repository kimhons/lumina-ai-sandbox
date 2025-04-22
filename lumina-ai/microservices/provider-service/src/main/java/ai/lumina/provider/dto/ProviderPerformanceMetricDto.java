package ai.lumina.provider.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProviderPerformanceMetricDto {
    private Long id;
    private Long providerId;
    private Long modelId;
    private String metricName;
    private Double metricValue;
    private LocalDateTime timestamp;
    private String context;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
