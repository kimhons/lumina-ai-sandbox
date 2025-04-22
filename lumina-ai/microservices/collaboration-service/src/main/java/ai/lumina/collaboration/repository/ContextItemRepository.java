package ai.lumina.collaboration.repository;

import ai.lumina.collaboration.model.ContextItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Repository for managing ContextItem entities.
 */
@Repository
public interface ContextItemRepository extends JpaRepository<ContextItem, Long> {

    /**
     * Find a context item by context ID.
     *
     * @param contextId the context ID
     * @return the context item
     */
    Optional<ContextItem> findByContextId(String contextId);

    /**
     * Find context items by key.
     *
     * @param key the context key
     * @return list of context items
     */
    List<ContextItem> findByKey(String key);

    /**
     * Find context items by context type.
     *
     * @param contextType the context type
     * @return list of context items
     */
    List<ContextItem> findByContextType(ContextItem.ContextType contextType);

    /**
     * Find context items by scope and scope ID.
     *
     * @param scope the context scope
     * @param scopeId the scope ID
     * @return list of context items
     */
    List<ContextItem> findByScopeAndScopeId(ContextItem.ContextScope scope, String scopeId);

    /**
     * Find context items by agent ID.
     *
     * @param agentId the agent ID
     * @return list of context items
     */
    List<ContextItem> findByAgentId(String agentId);

    /**
     * Find context items that have not expired.
     *
     * @param currentTime the current time
     * @return list of context items
     */
    List<ContextItem> findByExpiresAtIsNullOrExpiresAtGreaterThan(LocalDateTime currentTime);

    /**
     * Find context items by scope, scope ID, and context type.
     *
     * @param scope the context scope
     * @param scopeId the scope ID
     * @param contextType the context type
     * @return list of context items
     */
    List<ContextItem> findByScopeAndScopeIdAndContextType(
            ContextItem.ContextScope scope, 
            String scopeId, 
            ContextItem.ContextType contextType);

    /**
     * Find context items by key containing a specific string.
     *
     * @param keyPattern the key pattern to search for
     * @return list of context items
     */
    List<ContextItem> findByKeyContaining(String keyPattern);

    /**
     * Find context items accessible to an agent.
     * This includes items where the agent is the creator or items with appropriate scope.
     *
     * @param agentId the agent ID
     * @return list of context items
     */
    @Query("SELECT c FROM ContextItem c WHERE c.agentId = :agentId OR " +
           "(c.scope = ai.lumina.collaboration.model.ContextItem$ContextScope.AGENT AND c.scopeId = :agentId) OR " +
           "c.scope = ai.lumina.collaboration.model.ContextItem$ContextScope.GLOBAL OR " +
           "EXISTS (SELECT 1 FROM AgentTeam t JOIN t.members m WHERE m = :agentId AND " +
           "c.scope = ai.lumina.collaboration.model.ContextItem$ContextScope.TEAM AND c.scopeId = t.teamId)")
    List<ContextItem> findAccessibleToAgent(@Param("agentId") String agentId);
}
