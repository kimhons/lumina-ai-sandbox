package ai.lumina.collaboration.repository;

import ai.lumina.collaboration.model.LearningEvent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.Set;

/**
 * Repository for managing LearningEvent entities.
 */
@Repository
public interface LearningEventRepository extends JpaRepository<LearningEvent, Long> {

    /**
     * Find a learning event by event ID.
     *
     * @param eventId the event ID
     * @return the learning event
     */
    Optional<LearningEvent> findByEventId(String eventId);

    /**
     * Find learning events by event type.
     *
     * @param eventType the event type
     * @return list of learning events
     */
    List<LearningEvent> findByEventType(LearningEvent.LearningEventType eventType);

    /**
     * Find learning events by agent ID.
     *
     * @param agentId the agent ID
     * @return list of learning events
     */
    List<LearningEvent> findByAgentId(String agentId);

    /**
     * Find learning events by task ID.
     *
     * @param taskId the task ID
     * @return list of learning events
     */
    List<LearningEvent> findByTaskId(String taskId);

    /**
     * Find learning events by team ID.
     *
     * @param teamId the team ID
     * @return list of learning events
     */
    List<LearningEvent> findByTeamId(String teamId);

    /**
     * Find learning events with importance above a threshold.
     *
     * @param minImportance the minimum importance
     * @return list of learning events
     */
    List<LearningEvent> findByImportanceGreaterThanEqual(Float minImportance);

    /**
     * Find learning events created after a specific time.
     *
     * @param time the time threshold
     * @return list of learning events
     */
    List<LearningEvent> findByCreatedAtGreaterThan(LocalDateTime time);

    /**
     * Find learning events that are related to a specific event.
     *
     * @param eventId the related event ID
     * @return list of learning events
     */
    @Query("SELECT e FROM LearningEvent e JOIN e.relatedEvents r WHERE r = :eventId")
    List<LearningEvent> findByRelatedEvent(@Param("eventId") String eventId);

    /**
     * Find learning events by agent ID and event type.
     *
     * @param agentId the agent ID
     * @param eventType the event type
     * @return list of learning events
     */
    List<LearningEvent> findByAgentIdAndEventType(String agentId, LearningEvent.LearningEventType eventType);

    /**
     * Find learning events by team ID and event type.
     *
     * @param teamId the team ID
     * @param eventType the event type
     * @return list of learning events
     */
    List<LearningEvent> findByTeamIdAndEventType(String teamId, LearningEvent.LearningEventType eventType);

    /**
     * Find learning events accessible to an agent.
     * This includes events created by the agent or events related to teams the agent is a member of.
     *
     * @param agentId the agent ID
     * @return list of learning events
     */
    @Query("SELECT e FROM LearningEvent e WHERE e.agentId = :agentId OR " +
           "EXISTS (SELECT 1 FROM AgentTeam t JOIN t.members m WHERE m = :agentId AND e.teamId = t.teamId)")
    List<LearningEvent> findAccessibleToAgent(@Param("agentId") String agentId);
}
