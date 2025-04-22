package ai.lumina.collaboration.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

/**
 * Entity representing a memory item in the collaboration system.
 * Contains information about shared memory between agents.
 */
@Entity
@Table(name = "memory_items")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MemoryItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "memory_id", nullable = false, unique = true)
    private String memoryId;

    @Column(name = "key", nullable = false)
    private String key;

    @Column(name = "value_json", columnDefinition = "json", nullable = false)
    private String valueJson;

    @Column(name = "memory_type", nullable = false)
    @Enumerated(EnumType.STRING)
    private MemoryType memoryType;

    @Column(name = "scope", nullable = false)
    @Enumerated(EnumType.STRING)
    private MemoryScope scope;

    @Column(name = "scope_id", nullable = false)
    private String scopeId;

    @Column(name = "agent_id")
    private String agentId;

    @Column(name = "importance")
    private Float importance;

    @ElementCollection
    @CollectionTable(name = "memory_tags", 
                    joinColumns = @JoinColumn(name = "memory_id"))
    @Column(name = "tag")
    private Set<String> tags = new HashSet<>();

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "accessed_at")
    private LocalDateTime accessedAt;

    @Column(name = "access_count")
    private Integer accessCount;

    /**
     * Enum representing the type of memory.
     */
    public enum MemoryType {
        FACTUAL,
        PROCEDURAL,
        EPISODIC,
        SEMANTIC,
        CONTEXTUAL
    }

    /**
     * Enum representing the scope of memory.
     */
    public enum MemoryScope {
        AGENT,
        TEAM,
        TASK,
        GLOBAL
    }
}
