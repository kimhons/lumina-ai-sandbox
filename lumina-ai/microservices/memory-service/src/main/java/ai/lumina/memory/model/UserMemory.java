package ai.lumina.memory.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Represents a user's memory across multiple sessions.
 * This entity stores persistent memory that survives across different conversation sessions.
 */
@Entity
@Table(name = "user_memories")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserMemory {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "key", nullable = false)
    private String key;

    @Column(name = "value", columnDefinition = "TEXT", nullable = false)
    private String value;

    @Column(name = "memory_type", nullable = false)
    private String memoryType;

    @Column(name = "embedding", columnDefinition = "TEXT")
    private String embedding;

    @Column(name = "last_accessed")
    private LocalDateTime lastAccessed;

    @Column(name = "access_count")
    private Integer accessCount;

    @Column(name = "importance_score")
    private Double importanceScore;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "expires_at")
    private LocalDateTime expiresAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        accessCount = 0;
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    /**
     * Record an access to this memory
     */
    public void recordAccess() {
        lastAccessed = LocalDateTime.now();
        accessCount++;
    }
}
