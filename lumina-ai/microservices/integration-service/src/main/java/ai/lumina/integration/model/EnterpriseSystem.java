package ai.lumina.integration.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Entity representing an enterprise system integration configuration.
 */
@Entity
@Table(name = "enterprise_systems")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EnterpriseSystem {

    @Id
    @Column(name = "system_id", nullable = false)
    private String systemId;

    @Column(name = "system_type", nullable = false)
    private String systemType;

    @Column(name = "name", nullable = false)
    private String name;

    @Column(name = "description")
    private String description;

    @Column(name = "enabled")
    private boolean enabled;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @ElementCollection
    @CollectionTable(name = "enterprise_system_connection_params", 
                    joinColumns = @JoinColumn(name = "system_id"))
    @MapKeyColumn(name = "param_name")
    @Column(name = "param_value")
    private Map<String, String> connectionParams = new HashMap<>();

    @ElementCollection
    @CollectionTable(name = "enterprise_system_auth_params", 
                    joinColumns = @JoinColumn(name = "system_id"))
    @MapKeyColumn(name = "param_name")
    @Column(name = "param_value")
    private Map<String, String> authParams = new HashMap<>();

    @ElementCollection
    @CollectionTable(name = "enterprise_system_transform_params", 
                    joinColumns = @JoinColumn(name = "system_id"))
    @MapKeyColumn(name = "param_name")
    @Column(name = "param_value", columnDefinition = "TEXT")
    private Map<String, String> transformParams = new HashMap<>();

    @ElementCollection
    @CollectionTable(name = "enterprise_system_metadata", 
                    joinColumns = @JoinColumn(name = "system_id"))
    @MapKeyColumn(name = "meta_key")
    @Column(name = "meta_value")
    private Map<String, String> metadata = new HashMap<>();

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
