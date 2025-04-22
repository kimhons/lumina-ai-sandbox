package ai.lumina.provider.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "provider_models")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProviderModel {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "provider_id", nullable = false)
    private Provider provider;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private String modelId;

    @Column(length = 1000)
    private String description;

    @Column(name = "max_tokens")
    private Integer maxTokens;

    @Column(name = "context_window")
    private Integer contextWindow;

    @Column(name = "cost_per_1k_tokens_input")
    private Double costPer1kTokensInput;

    @Column(name = "cost_per_1k_tokens_output")
    private Double costPer1kTokensOutput;

    @Column(name = "supports_streaming")
    private boolean supportsStreaming;

    @Column(name = "supports_functions")
    private boolean supportsFunctions;

    @Column(name = "supports_vision")
    private boolean supportsVision;

    @Column(name = "supports_embeddings")
    private boolean supportsEmbeddings;

    @Column(nullable = false)
    private boolean enabled;

    @Column(name = "performance_rating")
    private Double performanceRating;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
