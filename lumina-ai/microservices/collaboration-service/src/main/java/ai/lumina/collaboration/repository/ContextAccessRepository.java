package ai.lumina.collaboration.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import ai.lumina.collaboration.model.ContextAccess;

/**
 * Repository for context access operations.
 */
@Repository
public interface ContextAccessRepository extends JpaRepository<ContextAccess, Long> {
    
    /**
     * Find access entries by agent ID.
     * 
     * @param agentId The agent ID
     * @return List of matching access entries
     */
    java.util.List<ContextAccess> findByAgentId(String agentId);
    
    /**
     * Find access entries by context ID.
     * 
     * @param contextId The context ID
     * @return List of matching access entries
     */
    java.util.List<ContextAccess> findByContextId(String contextId);
    
    /**
     * Find access entries by agent ID and context ID.
     * 
     * @param agentId The agent ID
     * @param contextId The context ID
     * @return List of matching access entries
     */
    java.util.List<ContextAccess> findByAgentIdAndContextId(String agentId, String contextId);
}
