package ai.lumina.collaboration.repository;

import ai.lumina.collaboration.model.Negotiation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Repository interface for Negotiation entity operations.
 */
@Repository
public interface NegotiationRepository extends JpaRepository<Negotiation, String> {

    /**
     * Find negotiations by type.
     *
     * @param type The negotiation type to search for
     * @return List of negotiations with the specified type
     */
    List<Negotiation> findByType(String type);

    /**
     * Find negotiations by status.
     *
     * @param status The status to search for
     * @return List of negotiations with the specified status
     */
    List<Negotiation> findByStatus(String status);

    /**
     * Find negotiations by initiator agent ID.
     *
     * @param initiatorId The initiator agent ID to search for
     * @return List of negotiations initiated by the specified agent
     */
    @Query("SELECT n FROM Negotiation n WHERE n.initiator.id = :initiatorId")
    List<Negotiation> findByInitiatorId(@Param("initiatorId") String initiatorId);

    /**
     * Find negotiations by participant agent ID.
     *
     * @param participantId The participant agent ID to search for
     * @return List of negotiations that include the specified agent as a participant
     */
    @Query("SELECT n FROM Negotiation n JOIN n.participants p WHERE p.id = :participantId")
    List<Negotiation> findByParticipantId(@Param("participantId") String participantId);

    /**
     * Find negotiations by task ID.
     *
     * @param taskId The task ID to search for
     * @return List of negotiations related to the specified task
     */
    @Query("SELECT n FROM Negotiation n WHERE n.task.id = :taskId")
    List<Negotiation> findByTaskId(@Param("taskId") String taskId);

    /**
     * Find active negotiations.
     *
     * @return List of active negotiations (pending or in progress)
     */
    @Query("SELECT n FROM Negotiation n WHERE n.status = 'PENDING' OR n.status = 'IN_PROGRESS'")
    List<Negotiation> findActiveNegotiations();

    /**
     * Find negotiations by outcome.
     *
     * @param outcome The outcome to search for
     * @return List of negotiations with the specified outcome
     */
    List<Negotiation> findByOutcome(String outcome);

    /**
     * Find negotiations started after a specific date.
     *
     * @param startDate The start date to compare against
     * @return List of negotiations started after the specified date
     */
    List<Negotiation> findByStartedAtAfter(LocalDateTime startDate);

    /**
     * Find negotiations completed before a specific date.
     *
     * @param endDate The end date to compare against
     * @return List of negotiations completed before the specified date
     */
    List<Negotiation> findByCompletedAtBefore(LocalDateTime endDate);

    /**
     * Find negotiations by current round.
     *
     * @param round The current round to search for
     * @return List of negotiations at the specified round
     */
    List<Negotiation> findByCurrentRound(int round);

    /**
     * Find long-running active negotiations.
     *
     * @param thresholdTime The threshold time to compare against
     * @return List of active negotiations that started before the threshold time
     */
    @Query("SELECT n FROM Negotiation n WHERE (n.status = 'PENDING' OR n.status = 'IN_PROGRESS') AND n.startedAt < :thresholdTime")
    List<Negotiation> findLongRunningActiveNegotiations(@Param("thresholdTime") LocalDateTime thresholdTime);
}
