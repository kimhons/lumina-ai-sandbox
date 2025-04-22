package ai.lumina.collaboration.repository;

import ai.lumina.collaboration.model.TaskRequirement;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.Set;

/**
 * Repository for managing TaskRequirement entities.
 */
@Repository
public interface TaskRequirementRepository extends JpaRepository<TaskRequirement, Long> {

    /**
     * Find a task requirement by task ID.
     *
     * @param taskId the task ID
     * @return the task requirement
     */
    Optional<TaskRequirement> findByTaskId(String taskId);

    /**
     * Find task requirements by status.
     *
     * @param status the task status
     * @return list of task requirements
     */
    List<TaskRequirement> findByStatus(TaskRequirement.TaskStatus status);

    /**
     * Find task requirements by creator ID.
     *
     * @param creatorId the creator ID
     * @return list of task requirements
     */
    List<TaskRequirement> findByCreatorId(String creatorId);

    /**
     * Find task requirements with a minimum priority.
     *
     * @param minPriority the minimum priority
     * @return list of task requirements
     */
    List<TaskRequirement> findByPriorityGreaterThanEqual(int minPriority);

    /**
     * Find task requirements that require a specific capability.
     *
     * @param capability the capability name
     * @return list of task requirements
     */
    @Query("SELECT tr FROM TaskRequirement tr JOIN tr.requiredCapabilities c WHERE KEY(c) = :capability")
    List<TaskRequirement> findByRequiredCapability(@Param("capability") String capability);

    /**
     * Find task requirements that require a specific capability with a minimum level.
     *
     * @param capability the capability name
     * @param minLevel the minimum capability level
     * @return list of task requirements
     */
    @Query("SELECT tr FROM TaskRequirement tr JOIN tr.requiredCapabilities c WHERE KEY(c) = :capability AND VALUE(c) >= :minLevel")
    List<TaskRequirement> findByRequiredCapabilityWithMinLevel(
            @Param("capability") String capability,
            @Param("minLevel") Float minLevel);

    /**
     * Find task requirements that have a specific domain specialization.
     *
     * @param specialization the domain specialization
     * @return list of task requirements
     */
    @Query("SELECT tr FROM TaskRequirement tr JOIN tr.domainSpecializations s WHERE s = :specialization")
    List<TaskRequirement> findByDomainSpecialization(@Param("specialization") String specialization);

    /**
     * Find task requirements with a maximum team size.
     *
     * @param maxSize the maximum team size
     * @return list of task requirements
     */
    List<TaskRequirement> findByMaxTeamSizeLessThanEqual(int maxSize);
}
