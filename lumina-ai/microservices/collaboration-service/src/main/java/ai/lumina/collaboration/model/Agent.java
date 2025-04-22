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
 * Represents an agent with specific capabilities that can participate in collaborative teams.
 */
@Entity
@Table(name = "agents")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Agent {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private String description;

    @Column(nullable = false)
    private String providerId;

    @Column(nullable = false)
    private String modelId;

    @ElementCollection
    @CollectionTable(name = "agent_capabilities", joinColumns = @JoinColumn(name = "agent_id"))
    @Column(name = "capability")
    private Set<String> capabilities = new HashSet<>();

    @Column(nullable = false)
    private double performanceRating;

    @Column(nullable = false)
    private int successfulTasks;

    @Column(nullable = false)
    private int totalTasks;

    @Column(nullable = false)
    private boolean available;

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
     * Calculate the success rate of this agent based on successful vs total tasks.
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
     * Check if the agent has a specific capability.
     * 
     * @param capability The capability to check for
     * @return True if the agent has the capability, false otherwise
     */
    public boolean hasCapability(String capability) {
        return capabilities.contains(capability);
    }

    /**
     * Add a capability to this agent.
     * 
     * @param capability The capability to add
     * @return True if the capability was added, false if it already existed
     */
    public boolean addCapability(String capability) {
        return capabilities.add(capability);
    }

    /**
     * Remove a capability from this agent.
     * 
     * @param capability The capability to remove
     * @return True if the capability was removed, false if it didn't exist
     */
    public boolean removeCapability(String capability) {
        return capabilities.remove(capability);
    }
}
