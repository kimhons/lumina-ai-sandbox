package ai.lumina.memory.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.GenericGenerator;

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entity representing a persistent memory item that persists across sessions.
 * Memory items store key information that should be remembered across different conversation sessions.
 */
@Entity
@Table(name = "memory_items")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PersistentMemory {

    @Id
    @GeneratedValue(generator = "UUID")
    @GenericGenerator(name = "UUID", strategy = "org.hibernate.id.UUIDGenerator")
    @Column(name = "id", updatable = false, nullable = false)
    private UUID id;

    @Column(name = "memory_key", nullable = false)
    private String key;

    @Column(name = "memory_value", columnDefinition = "TEXT", nullable = false)
    private String value;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "memory_type", nullable = false)
    private String memoryType;

    @Column(name = "importance_score", nullable = false)
    private Double importanceScore;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @Column(name = "last_accessed")
    private LocalDateTime lastAccessed;

    @Column(name = "access_count", nullable = false)
    private Integer accessCount;

    @Column(name = "expires_at")
    private LocalDateTime expiresAt;

    @Column(name = "embedding", columnDefinition = "TEXT")
    private String embeddingJson;

    /**
     * Record an access to this memory item.
     */
    @PreUpdate
    public void recordAccess() {
        this.lastAccessed = LocalDateTime.now();
        this.accessCount++;
    }

    /**
     * Check if the memory item has expired.
     *
     * @return True if the memory has expired, false otherwise
     */
    public boolean isExpired() {
        if (this.expiresAt == null) {
            return false;
        }
        return LocalDateTime.now().isAfter(this.expiresAt);
    }

    /**
     * Update the memory value.
     *
     * @param value New value for the memory
     */
    public void updateValue(String value) {
        this.value = value;
        this.updatedAt = LocalDateTime.now();
    }
}
