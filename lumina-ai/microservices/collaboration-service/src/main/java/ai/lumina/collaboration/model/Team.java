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
 * Represents a team of agents assembled for collaborative task execution.
 */
@Entity
@Table(name = "teams")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Team {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private String description;

    @ManyToMany
    @JoinTable(
        name = "team_agents",
        joinColumns = @JoinColumn(name = "team_id"),
        inverseJoinColumns = @JoinColumn(name = "agent_id")
    )
    private Set<Agent> agents = new HashSet<>();

    @OneToOne
    @JoinColumn(name = "leader_id")
    private Agent leader;

    @ElementCollection
    @CollectionTable(name = "team_capabilities", joinColumns = @JoinColumn(name = "team_id"))
    @Column(name = "capability")
    private Set<String> capabilities = new HashSet<>();

    @Column(nullable = false)
    private String status;

    @Column(nullable = false)
    private double performanceRating;

    @Column(nullable = false)
    private int successfulTasks;

    @Column(nullable = false)
    private int totalTasks;

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
     * Calculate the success rate of this team based on successful vs total tasks.
     * 
     * @return The success rate as a percentage (0-100)
     */
    @Transient
    public double getSuccessRate() {
        if (totalTasks == 0) {
            return 0.0;
        }
        return (double) successfulTasks / totalTasks * 100.0;
    }

    /**
     * Add an agent to the team.
     * 
     * @param agent The agent to add
     * @return True if the agent was added, false if already in team
     */
    public boolean addAgent(Agent agent) {
        boolean added = agents.add(agent);
        if (added) {
            // Update team capabilities based on agent capabilities
            capabilities.addAll(agent.getCapabilities());
        }
        return added;
    }

    /**
     * Remove an agent from the team.
     * 
     * @param agent The agent to remove
     * @return True if the agent was removed, false if not in team
     */
    public boolean removeAgent(Agent agent) {
        boolean removed = agents.remove(agent);
        if (removed) {
            // Recalculate team capabilities
            recalculateCapabilities();
        }
        return removed;
    }

    /**
     * Set the team leader.
     * 
     * @param agent The agent to set as leader
     * @return True if the leader was set, false if agent not in team
     */
    public boolean setTeamLeader(Agent agent) {
        if (agents.contains(agent)) {
            this.leader = agent;
            return true;
        }
        return false;
    }

    /**
     * Check if the team has a specific capability.
     * 
     * @param capability The capability to check for
     * @return True if the team has the capability, false otherwise
     */
    public boolean hasCapability(String capability) {
        return capabilities.contains(capability);
    }

    /**
     * Recalculate team capabilities based on member agents.
     */
    private void recalculateCapabilities() {
        capabilities.clear();
        for (Agent agent : agents) {
            capabilities.addAll(agent.getCapabilities());
        }
    }
}
