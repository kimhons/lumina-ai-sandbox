package ai.lumina.collaboration.repository;

import ai.lumina.collaboration.model.Task;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Set;

/**
 * Repository interface for Task entity operations.
 */
@Repository
public interface TaskRepository extends JpaRepository<Task, String> {

    /**
     * Find tasks by status.
     *
     * @param status The status to search for
     * @return List of tasks with the specified status
     */
    List<Task> findByStatus(String status);

    /**
     * Find tasks by priority.
     *
     * @param priority The priority level to search for
     * @return List of tasks with the specified priority
     */
    List<Task> findByPriority(int priority);

    /**
     * Find tasks by priority greater than or equal to a threshold.
     *
     * @param minPriority The minimum priority level
     * @return List of tasks with priority greater than or equal to the threshold
     */
    List<Task> findByPriorityGreaterThanEqual(int minPriority);

    /**
     * Find tasks by complexity.
     *
     * @param complexity The complexity level to search for
     * @return List of tasks with the specified complexity
     */
    List<Task> findByComplexity(int complexity);

    /**
     * Find tasks by assigned team ID.
     *
     * @param teamId The team ID to search for
     * @return List of tasks assigned to the specified team
     */
    @Query("SELECT t FROM Task t WHERE t.assignedTeam.id = :teamId")
    List<Task> findByAssignedTeamId(@Param("teamId") String teamId);

    /**
     * Find unassigned tasks.
     *
     * @return List of tasks that are not assigned to any team
     */
    @Query("SELECT t FROM Task t WHERE t.assignedTeam IS NULL")
    List<Task> findUnassignedTasks();

    /**
     * Find tasks with deadline before a specific date.
     *
     * @param deadline The deadline to compare against
     * @return List of tasks with deadline before the specified date
     */
    List<Task> findByDeadlineBefore(LocalDateTime deadline);

    /**
     * Find overdue tasks.
     *
     * @param currentTime The current time to compare against
     * @return List of tasks that are overdue
     */
    @Query("SELECT t FROM Task t WHERE t.deadline < :currentTime AND t.completedAt IS NULL")
    List<Task> findOverdueTasks(@Param("currentTime") LocalDateTime currentTime);

    /**
     * Find tasks requiring specific capabilities.
     *
     * @param capabilities The set of capabilities to search for
     * @return List of tasks that require all the specified capabilities
     */
    @Query("SELECT t FROM Task t JOIN t.requiredCapabilities c WHERE c IN :capabilities GROUP BY t HAVING COUNT(DISTINCT c) = :capabilityCount")
    List<Task> findByRequiredCapabilities(@Param("capabilities") Set<String> capabilities, @Param("capabilityCount") long capabilityCount);

    /**
     * Find tasks requiring at least one of the specified capabilities.
     *
     * @param capabilities The set of capabilities to search for
     * @return List of tasks that require at least one of the specified capabilities
     */
    @Query("SELECT DISTINCT t FROM Task t JOIN t.requiredCapabilities c WHERE c IN :capabilities")
    List<Task> findByAnyRequiredCapability(@Param("capabilities") Set<String> capabilities);

    /**
     * Find high-priority unassigned tasks.
     *
     * @param minPriority The minimum priority level
     * @return List of unassigned tasks with priority greater than or equal to the threshold
     */
    @Query("SELECT t FROM Task t WHERE t.assignedTeam IS NULL AND t.priority >= :minPriority ORDER BY t.priority DESC")
    List<Task> findHighPriorityUnassignedTasks(@Param("minPriority") int minPriority);
}
