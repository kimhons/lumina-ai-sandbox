package ai.lumina.collaboration.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Entity representing a context item in the collaboration system.
 * Contains information about shared context between agents.
 */
@Entity
@Table(name = "context_items")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ContextItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "context_id", nullable = false, unique = true)
    private String contextId;

    @Column(name = "key", nullable = false)
    private String key;

    @Column(name = "value_json", columnDefinition = "json", nullable = false)
    private String valueJson;

    @Column(name = "context_type", nullable = false)
    @Enumerated(EnumType.STRING)
    private ContextType contextType;

    @Column(name = "scope", nullable = false)
    @Enumerated(EnumType.STRING)
    private ContextScope scope;

    @Column(name = "scope_id", nullable = false)
    private String scopeId;

    @Column(name = "agent_id")
    private String agentId;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "expires_at")
    private LocalDateTime expiresAt;

    /**
     * Enum representing the type of context.
     */
    public enum ContextType {
        USER_INPUT,
        SYSTEM_STATE,
        TASK_DEFINITION,
        AGENT_KNOWLEDGE,
        EXTERNAL_INFORMATION
    }

    /**
     * Enum representing the scope of context.
     */
    public enum ContextScope {
        AGENT,
        TEAM,
        TASK,
        GLOBAL
    }
}
