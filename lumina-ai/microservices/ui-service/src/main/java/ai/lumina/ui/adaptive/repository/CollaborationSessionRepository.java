package ai.lumina.ui.adaptive.repository;

import ai.lumina.ui.adaptive.model.CollaborationSession;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository for managing collaboration sessions in the database
 */
@Repository
public interface CollaborationSessionRepository extends JpaRepository<CollaborationSession, Long> {
    
    /**
     * Find collaboration session by session ID
     * 
     * @param sessionId The unique ID of the collaboration session
     * @return Optional containing the collaboration session if found
     */
    Optional<CollaborationSession> findBySessionId(String sessionId);
    
    /**
     * Find active collaboration sessions for a user
     * 
     * @param userId The ID of the user
     * @param active Whether the session is active
     * @return List of active collaboration sessions for the user
     */
    List<CollaborationSession> findByParticipantsContainingAndActiveTrue(String userId);
    
    /**
     * Find collaboration sessions by type
     * 
     * @param type The type of collaboration session (e.g., "CAPTCHA_BYPASS")
     * @return List of collaboration sessions of the specified type
     */
    List<CollaborationSession> findBySessionType(String type);
}
