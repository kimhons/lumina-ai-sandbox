package ai.lumina.provider.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Set;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProviderDto {
    private Long id;
    private String name;
    private String apiEndpoint;
    private String apiVersion;
    private boolean enabled;
    private String description;
    private String authType;
    private Double costPer1kTokensInput;
    private Double costPer1kTokensOutput;
    private Integer maxTokens;
    private boolean supportsStreaming;
    private boolean supportsFunctions;
    private boolean supportsVision;
    private boolean supportsEmbeddings;
    private Set<ProviderModelDto> models;
    private Set<ProviderCapabilityDto> capabilities;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
