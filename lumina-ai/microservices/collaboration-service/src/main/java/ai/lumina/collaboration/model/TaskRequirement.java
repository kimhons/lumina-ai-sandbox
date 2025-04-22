package ai.lumina.collaboration.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Entity representing a task requirement in the collaboration system.
 * Contains information about the capabilities and specializations required for a task.
 */
@Entity
@Table(name = "task_requirements")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TaskRequirement {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "task_id", nullable = false, unique = true)
    private String taskId;

    @Column(name = "name", nullable = false)
    private String name;

    @Column(name = "description", length = 2000)
    private String description;

    /**
     * Map of required capabilities to their minimum levels (0.0 to 1.0)
     * Stored as JSON in the database
     */
    @ElementCollection
    @CollectionTable(name = "task_required_capabilities", 
                    joinColumns = @JoinColumn(name = "task_id"))
    @MapKeyColumn(name = "capability")
    @Column(name = "level")
    private Map<String, Float> requiredCapabilities = new HashMap<>();

    /**
     * Set of domain specializations relevant to the task
     */
    @ElementCollection
    @CollectionTable(name = "task_domain_specializations", 
                    joinColumns = @JoinColumn(name = "task_id"))
    @Column(name = "specialization")
    private Set<String> domainSpecializations = new HashSet<>();

    @Column(name = "priority")
    private int priority;

    @Column(name = "estimated_duration")
    private float estimatedDuration;

    @Column(name = "complexity")
    private int complexity;

    @Column(name = "min_team_size")
    private int minTeamSize;

    @Column(name = "max_team_size")
    private int maxTeamSize;

    @Column(name = "status")
    @Enumerated(EnumType.STRING)
    private TaskStatus status;

    @Column(name = "creator_id")
    private String creatorId;
    
    /**
     * Enum representing the status of a task.
     */
    public enum TaskStatus {
        CREATED,
        ASSIGNED,
        IN_PROGRESS,
        COMPLETED,
        FAILED,
        CANCELLED
    }
}
