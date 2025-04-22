package ai.lumina.collaboration.repository;

import ai.lumina.collaboration.model.Workflow;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Repository interface for Workflow entity operations.
 */
@Repository
public interface WorkflowRepository extends JpaRepository<Workflow, String> {

    /**
     * Find workflows by status.
     *
     * @param status The status to search for
     * @return List of workflows with the specified status
     */
    List<Workflow> findByStatus(String status);

    /**
     * Find workflows by name containing a substring.
     *
     * @param nameSubstring The substring to search for in workflow names
     * @return List of workflows with names containing the specified substring
     */
    List<Workflow> findByNameContaining(String nameSubstring);

    /**
     * Find active workflows.
     *
     * @return List of active workflows (pending or in progress)
     */
    @Query("SELECT w FROM Workflow w WHERE w.status = 'PENDING' OR w.status = 'IN_PROGRESS'")
    List<Workflow> findActiveWorkflows();

    /**
     * Find workflows started after a specific date.
     *
     * @param startDate The start date to compare against
     * @return List of workflows started after the specified date
     */
    List<Workflow> findByStartedAtAfter(LocalDateTime startDate);

    /**
     * Find workflows completed before a specific date.
     *
     * @param endDate The end date to compare against
     * @return List of workflows completed before the specified date
     */
    List<Workflow> findByCompletedAtBefore(LocalDateTime endDate);

    /**
     * Find workflows by current step index.
     *
     * @param stepIndex The current step index to search for
     * @return List of workflows at the specified step index
     */
    List<Workflow> findByCurrentStepIndex(int stepIndex);

    /**
     * Find long-running active workflows.
     *
     * @param thresholdTime The threshold time to compare against
     * @return List of active workflows that started before the threshold time
     */
    @Query("SELECT w FROM Workflow w WHERE (w.status = 'PENDING' OR w.status = 'IN_PROGRESS') AND w.startedAt < :thresholdTime")
    List<Workflow> findLongRunningActiveWorkflows(@Param("thresholdTime") LocalDateTime thresholdTime);

    /**
     * Find workflows with a specific number of steps.
     *
     * @param stepCount The number of steps to search for
     * @return List of workflows with the specified number of steps
     */
    @Query("SELECT w FROM Workflow w WHERE SIZE(w.steps) = :stepCount")
    List<Workflow> findByStepCount(@Param("stepCount") int stepCount);

    /**
     * Find workflows with high progress percentage.
     *
     * @param minStepIndex The minimum step index
     * @return List of in-progress workflows with current step index greater than or equal to the threshold
     */
    @Query("SELECT w FROM Workflow w WHERE w.status = 'IN_PROGRESS' AND w.currentStepIndex >= :minStepIndex")
    List<Workflow> findHighProgressWorkflows(@Param("minStepIndex") int minStepIndex);

    /**
     * Find recently completed workflows.
     *
     * @param thresholdTime The threshold time to compare against
     * @return List of completed workflows that were completed after the threshold time
     */
    @Query("SELECT w FROM Workflow w WHERE w.status = 'COMPLETED' AND w.completedAt > :thresholdTime")
    List<Workflow> findRecentlyCompletedWorkflows(@Param("thresholdTime") LocalDateTime thresholdTime);
}
