package ai.lumina.collaboration.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import ai.lumina.collaboration.model.ContextVersion;

/**
 * Repository for context version operations.
 */
@Repository
public interface ContextVersionRepository extends JpaRepository<ContextVersion, String> {
    
    /**
     * Find versions by agent ID.
     * 
     * @param agentId The agent ID
     * @return List of matching versions
     */
    java.util.List<ContextVersion> findByAgentId(String agentId);
    
    /**
     * Find versions by parent version ID.
     * 
     * @param parentVersionId The parent version ID
     * @return List of matching versions
     */
    java.util.List<ContextVersion> findByParentVersionId(String parentVersionId);
}
