package ai.lumina.collaboration.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Entity representing an agent profile in the collaboration system.
 * Contains information about the agent's capabilities and specializations.
 */
@Entity
@Table(name = "agent_profiles")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AgentProfile {

    @Id
    @Column(name = "agent_id", nullable = false)
    private String agentId;

    @Column(name = "name", nullable = false)
    private String name;

    /**
     * Map of capabilities to their levels (0.0 to 1.0)
     * Stored as JSON in the database
     */
    @ElementCollection
    @CollectionTable(name = "agent_capabilities", 
                    joinColumns = @JoinColumn(name = "agent_id"))
    @MapKeyColumn(name = "capability")
    @Column(name = "level")
    private Map<String, Float> capabilities;

    /**
     * Set of domain specializations
     */
    @ElementCollection
    @CollectionTable(name = "agent_specializations", 
                    joinColumns = @JoinColumn(name = "agent_id"))
    @Column(name = "specialization")
    private Set<String> specializations = new HashSet<>();

    @Column(name = "provider_id")
    private String providerId;

    @Column(name = "is_active")
    private boolean active;

    @Column(name = "description", length = 1000)
    private String description;
}
