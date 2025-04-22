package ai.lumina.collaboration.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

/**
 * Represents a role within a team with specific responsibilities and required capabilities.
 */
@Entity
@Table(name = "roles")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Role {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private String description;

    @ElementCollection
    @CollectionTable(name = "role_required_capabilities", joinColumns = @JoinColumn(name = "role_id"))
    @Column(name = "capability")
    private Set<String> requiredCapabilities = new HashSet<>();

    @Column(nullable = false)
    private int priority;

    @ManyToOne
    @JoinColumn(name = "team_id")
    private Team team;

    @ManyToOne
    @JoinColumn(name = "assigned_agent_id")
    private Agent assignedAgent;

    @Column(nullable = false)
    private boolean filled;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    /**
     * Check if an agent is qualified for this role based on capabilities.
     * 
     * @param agent The agent to check
     * @return True if the agent has all required capabilities, false otherwise
     */
    public boolean isAgentQualified(Agent agent) {
        for (String capability : requiredCapabilities) {
            if (!agent.hasCapability(capability)) {
                return false;
            }
        }
        return true;
    }

    /**
     * Assign an agent to this role.
     * 
     * @param agent The agent to assign
     * @return True if assignment was successful, false if agent not qualified
     */
    public boolean assignAgent(Agent agent) {
        if (isAgentQualified(agent)) {
            this.assignedAgent = agent;
            this.filled = true;
            return true;
        }
        return false;
    }

    /**
     * Unassign the current agent from this role.
     */
    public void unassignAgent() {
        this.assignedAgent = null;
        this.filled = false;
    }

    /**
     * Add a required capability to this role.
     * 
     * @param capability The capability to add
     * @return True if the capability was added, false if it already existed
     */
    public boolean addRequiredCapability(String capability) {
        return requiredCapabilities.add(capability);
    }

    /**
     * Remove a required capability from this role.
     * 
     * @param capability The capability to remove
     * @return True if the capability was removed, false if it didn't exist
     */
    public boolean removeRequiredCapability(String capability) {
        return requiredCapabilities.remove(capability);
    }
}
