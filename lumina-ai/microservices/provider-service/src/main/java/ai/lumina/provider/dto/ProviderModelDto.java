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
public class ProviderModelDto {
    private Long id;
    private Long providerId;
    private String name;
    private String modelId;
    private String description;
    private Integer maxTokens;
    private Integer contextWindow;
    private Double costPer1kTokensInput;
    private Double costPer1kTokensOutput;
    private boolean supportsStreaming;
    private boolean supportsFunctions;
    private boolean supportsVision;
    private boolean supportsEmbeddings;
    private boolean enabled;
    private Double performanceRating;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
