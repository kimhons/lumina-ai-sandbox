package ai.lumina.learning.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import ai.lumina.learning.model.ProblemSolvingSession;

/**
 * Repository interface for ProblemSolvingSession entities.
 * Provides CRUD operations and custom queries for problem solving sessions.
 */
@Repository
public interface ProblemSolvingSessionRepository extends JpaRepository<ProblemSolvingSession, String> {
    
    /**
     * Find sessions by problem type.
     * 
     * @param problemType The problem type
     * @return List of sessions with the specified problem type
     */
    Iterable<ProblemSolvingSession> findByProblemType(ProblemSolvingSession.ProblemType problemType);
    
    /**
     * Find sessions by status.
     * 
     * @param status The session status
     * @return List of sessions with the specified status
     */
    Iterable<ProblemSolvingSession> findByStatus(ProblemSolvingSession.SessionStatus status);
    
    /**
     * Find sessions by team ID.
     * 
     * @param teamId The team ID
     * @return List of sessions for the specified team
     */
    Iterable<ProblemSolvingSession> findByTeamId(String teamId);
    
    /**
     * Find sessions by context ID.
     * 
     * @param contextId The context ID
     * @return List of sessions for the specified context
     */
    Iterable<ProblemSolvingSession> findByContextId(String contextId);
    
    /**
     * Find sessions by problem ID.
     * 
     * @param problemId The problem ID
     * @return List of sessions for the specified problem
     */
    Iterable<ProblemSolvingSession> findByProblemId(String problemId);
    
    /**
     * Find sessions by domain.
     * 
     * @param domain The domain
     * @return List of sessions in the specified domain
     */
    Iterable<ProblemSolvingSession> findByDomain(String domain);
}
