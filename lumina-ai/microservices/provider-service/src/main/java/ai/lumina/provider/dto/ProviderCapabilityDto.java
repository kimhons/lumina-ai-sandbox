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
public class ProviderCapabilityDto {
    private Long id;
    private Long providerId;
    private String name;
    private String category;
    private String description;
    private Integer capabilityLevel;
    private Double benchmarkScore;
    private boolean isVerified;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
