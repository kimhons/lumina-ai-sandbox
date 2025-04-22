package ai.lumina.memory.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Represents a compressed context in the memory system.
 * This entity stores summarized or compressed versions of conversation contexts
 * to optimize token usage while preserving important information.
 */
@Entity
@Table(name = "compressed_contexts")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CompressedContext {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "original_content", columnDefinition = "TEXT", nullable = false)
    private String originalContent;

    @Column(name = "compressed_content", columnDefinition = "TEXT", nullable = false)
    private String compressedContent;

    @Column(name = "compression_ratio")
    private Double compressionRatio;

    @Column(name = "compression_method", nullable = false)
    private String compressionMethod;

    @Column(name = "user_id")
    private String userId;

    @Column(name = "session_id")
    private String sessionId;

    @Column(name = "original_token_count")
    private Integer originalTokenCount;

    @Column(name = "compressed_token_count")
    private Integer compressedTokenCount;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (originalContent != null && compressedContent != null) {
            // Simple approximation of compression ratio
            compressionRatio = (double) compressedContent.length() / originalContent.length();
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
        if (originalContent != null && compressedContent != null) {
            // Update compression ratio if content changes
            compressionRatio = (double) compressedContent.length() / originalContent.length();
        }
    }
}
