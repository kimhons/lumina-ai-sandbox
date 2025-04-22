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
 * Represents a task that needs to be executed by a team of agents.
 */
@Entity
@Table(name = "tasks")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Task {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, length = 2000)
    private String description;

    @Column(nullable = false)
    private String status;

    @Column(nullable = false)
    private int priority;

    @Column(nullable = false)
    private int complexity;

    @ElementCollection
    @CollectionTable(name = "task_required_capabilities", joinColumns = @JoinColumn(name = "task_id"))
    @Column(name = "capability")
    private Set<String> requiredCapabilities = new HashSet<>();

    @ManyToOne
    @JoinColumn(name = "assigned_team_id")
    private Team assignedTeam;

    @Column(nullable = true)
    private LocalDateTime deadline;

    @Column(nullable = true)
    private LocalDateTime startedAt;

    @Column(nullable = true)
    private LocalDateTime completedAt;

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
     * Check if a team is qualified for this task based on capabilities.
     * 
     * @param team The team to check
     * @return True if the team has all required capabilities, false otherwise
     */
    public boolean isTeamQualified(Team team) {
        for (String capability : requiredCapabilities) {
            if (!team.hasCapability(capability)) {
                return false;
            }
        }
        return true;
    }

    /**
     * Assign a team to this task.
     * 
     * @param team The team to assign
     * @return True if assignment was successful, false if team not qualified
     */
    public boolean assignTeam(Team team) {
        if (isTeamQualified(team)) {
            this.assignedTeam = team;
            return true;
        }
        return false;
    }

    /**
     * Start the task execution.
     * 
     * @return True if the task was started, false if already started or no team assigned
     */
    public boolean startTask() {
        if (assignedTeam != null && startedAt == null) {
            this.startedAt = LocalDateTime.now();
            this.status = "IN_PROGRESS";
            return true;
        }
        return false;
    }

    /**
     * Complete the task.
     * 
     * @param successful Whether the task was completed successfully
     * @return True if the task was completed, false if not started or already completed
     */
    public boolean completeTask(boolean successful) {
        if (startedAt != null && completedAt == null) {
            this.completedAt = LocalDateTime.now();
            this.status = successful ? "COMPLETED" : "FAILED";
            
            // Update team statistics if assigned
            if (assignedTeam != null) {
                assignedTeam.setTotalTasks(assignedTeam.getTotalTasks() + 1);
                if (successful) {
                    assignedTeam.setSuccessfulTasks(assignedTeam.getSuccessfulTasks() + 1);
                }
            }
            
            return true;
        }
        return false;
    }

    /**
     * Add a required capability to this task.
     * 
     * @param capability The capability to add
     * @return True if the capability was added, false if it already existed
     */
    public boolean addRequiredCapability(String capability) {
        return requiredCapabilities.add(capability);
    }

    /**
     * Remove a required capability from this task.
     * 
     * @param capability The capability to remove
     * @return True if the capability was removed, false if it didn't exist
     */
    public boolean removeRequiredCapability(String capability) {
        return requiredCapabilities.remove(capability);
    }

    /**
     * Check if the task is overdue.
     * 
     * @return True if the task is overdue, false otherwise
     */
    @Transient
    public boolean isOverdue() {
        if (deadline == null || completedAt != null) {
            return false;
        }
        return LocalDateTime.now().isAfter(deadline);
    }

    /**
     * Get the duration of the task execution in minutes.
     * 
     * @return The duration in minutes, or -1 if the task hasn't been started or completed
     */
    @Transient
    public long getDurationMinutes() {
        if (startedAt == null) {
            return -1;
        }
        
        LocalDateTime endTime = completedAt != null ? completedAt : LocalDateTime.now();
        return java.time.Duration.between(startedAt, endTime).toMinutes();
    }
}
