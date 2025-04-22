package ai.lumina.learning.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import ai.lumina.learning.model.CollaborativeLearningSession;

/**
 * Repository interface for CollaborativeLearningSession entities.
 * Provides CRUD operations and custom queries for collaborative learning sessions.
 */
@Repository
public interface CollaborativeLearningSessionRepository extends JpaRepository<CollaborativeLearningSession, String> {
    
    /**
     * Find sessions by learning type.
     * 
     * @param learningType The learning type
     * @return List of sessions with the specified learning type
     */
    Iterable<CollaborativeLearningSession> findByLearningType(CollaborativeLearningSession.LearningType learningType);
    
    /**
     * Find sessions by status.
     * 
     * @param status The session status
     * @return List of sessions with the specified status
     */
    Iterable<CollaborativeLearningSession> findByStatus(CollaborativeLearningSession.SessionStatus status);
    
    /**
     * Find sessions by team ID.
     * 
     * @param teamId The team ID
     * @return List of sessions for the specified team
     */
    Iterable<CollaborativeLearningSession> findByTeamId(String teamId);
    
    /**
     * Find sessions by context ID.
     * 
     * @param contextId The context ID
     * @return List of sessions for the specified context
     */
    Iterable<CollaborativeLearningSession> findByContextId(String contextId);
    
    /**
     * Find sessions by task ID.
     * 
     * @param taskId The task ID
     * @return List of sessions for the specified task
     */
    Iterable<CollaborativeLearningSession> findByTaskId(String taskId);
}
