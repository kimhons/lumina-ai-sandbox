package ai.lumina.memory.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/**
 * Represents a topic in the hierarchical memory system.
 * Topics organize memory items into a semantic hierarchy for better retrieval and context management.
 */
@Entity
@Table(name = "memory_topics")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Topic {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "name", nullable = false)
    private String name;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "embedding", columnDefinition = "TEXT")
    private String embedding;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_id")
    private Topic parent;

    @OneToMany(mappedBy = "parent", cascade = CascadeType.ALL, orphanRemoval = true)
    private Set<Topic> children = new HashSet<>();

    @Column(name = "user_id")
    private String userId;

    @Column(name = "importance_score")
    private Double importanceScore;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    /**
     * Add a child topic to this topic
     * 
     * @param child The child topic to add
     */
    public void addChild(Topic child) {
        children.add(child);
        child.setParent(this);
    }

    /**
     * Remove a child topic from this topic
     * 
     * @param child The child topic to remove
     */
    public void removeChild(Topic child) {
        children.remove(child);
        child.setParent(null);
    }
}
