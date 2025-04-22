package ai.lumina.provider.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

@Entity
@Table(name = "providers")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Provider {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name;

    @Column(nullable = false)
    private String apiEndpoint;

    @Column(nullable = false)
    private String apiVersion;

    @Column(nullable = false)
    private boolean enabled;

    @Column(length = 1000)
    private String description;

    @Column(name = "auth_type")
    @Enumerated(EnumType.STRING)
    private AuthType authType;

    @Column(name = "cost_per_1k_tokens_input")
    private Double costPer1kTokensInput;

    @Column(name = "cost_per_1k_tokens_output")
    private Double costPer1kTokensOutput;

    @Column(name = "max_tokens")
    private Integer maxTokens;

    @Column(name = "supports_streaming")
    private boolean supportsStreaming;

    @Column(name = "supports_functions")
    private boolean supportsFunctions;

    @Column(name = "supports_vision")
    private boolean supportsVision;

    @Column(name = "supports_embeddings")
    private boolean supportsEmbeddings;

    @OneToMany(mappedBy = "provider", cascade = CascadeType.ALL, orphanRemoval = true)
    private Set<ProviderModel> models = new HashSet<>();

    @OneToMany(mappedBy = "provider", cascade = CascadeType.ALL, orphanRemoval = true)
    private Set<ProviderCapability> capabilities = new HashSet<>();

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    public enum AuthType {
        API_KEY,
        OAUTH,
        BASIC,
        NONE
    }
}
