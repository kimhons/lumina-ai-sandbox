package ai.lumina.collaboration.repository;

import ai.lumina.collaboration.model.MemoryItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.Set;

/**
 * Repository for managing MemoryItem entities.
 */
@Repository
public interface MemoryItemRepository extends JpaRepository<MemoryItem, Long> {

    /**
     * Find a memory item by memory ID.
     *
     * @param memoryId the memory ID
     * @return the memory item
     */
    Optional<MemoryItem> findByMemoryId(String memoryId);

    /**
     * Find memory items by key.
     *
     * @param key the memory key
     * @return list of memory items
     */
    List<MemoryItem> findByKey(String key);

    /**
     * Find memory items by memory type.
     *
     * @param memoryType the memory type
     * @return list of memory items
     */
    List<MemoryItem> findByMemoryType(MemoryItem.MemoryType memoryType);

    /**
     * Find memory items by scope and scope ID.
     *
     * @param scope the memory scope
     * @param scopeId the scope ID
     * @return list of memory items
     */
    List<MemoryItem> findByScopeAndScopeId(MemoryItem.MemoryScope scope, String scopeId);

    /**
     * Find memory items by agent ID.
     *
     * @param agentId the agent ID
     * @return list of memory items
     */
    List<MemoryItem> findByAgentId(String agentId);

    /**
     * Find memory items with importance above a threshold.
     *
     * @param minImportance the minimum importance
     * @return list of memory items
     */
    List<MemoryItem> findByImportanceGreaterThanEqual(Float minImportance);

    /**
     * Find memory items by tag.
     *
     * @param tag the tag
     * @return list of memory items
     */
    @Query("SELECT m FROM MemoryItem m JOIN m.tags t WHERE t = :tag")
    List<MemoryItem> findByTag(@Param("tag") String tag);

    /**
     * Find memory items by multiple tags (must have all tags).
     *
     * @param tags the set of tags
     * @return list of memory items
     */
    @Query("SELECT m FROM MemoryItem m WHERE " +
           "(SELECT COUNT(DISTINCT t) FROM MemoryItem m2 JOIN m2.tags t " +
           "WHERE m2 = m AND t IN :tags) = :tagCount")
    List<MemoryItem> findByAllTags(
            @Param("tags") Set<String> tags,
            @Param("tagCount") long tagCount);

    /**
     * Find memory items by multiple tags (must have at least one tag).
     *
     * @param tags the set of tags
     * @return list of memory items
     */
    @Query("SELECT DISTINCT m FROM MemoryItem m JOIN m.tags t WHERE t IN :tags")
    List<MemoryItem> findByAnyTag(@Param("tags") Set<String> tags);

    /**
     * Find memory items accessed after a specific time.
     *
     * @param time the time threshold
     * @return list of memory items
     */
    List<MemoryItem> findByAccessedAtGreaterThan(LocalDateTime time);

    /**
     * Find memory items with access count above a threshold.
     *
     * @param minCount the minimum access count
     * @return list of memory items
     */
    List<MemoryItem> findByAccessCountGreaterThanEqual(Integer minCount);

    /**
     * Find memory items accessible to an agent.
     * This includes items where the agent is the creator or items with appropriate scope.
     *
     * @param agentId the agent ID
     * @return list of memory items
     */
    @Query("SELECT m FROM MemoryItem m WHERE m.agentId = :agentId OR " +
           "(m.scope = ai.lumina.collaboration.model.MemoryItem$MemoryScope.AGENT AND m.scopeId = :agentId) OR " +
           "m.scope = ai.lumina.collaboration.model.MemoryItem$MemoryScope.GLOBAL OR " +
           "EXISTS (SELECT 1 FROM AgentTeam t JOIN t.members mem WHERE mem = :agentId AND " +
           "m.scope = ai.lumina.collaboration.model.MemoryItem$MemoryScope.TEAM AND m.scopeId = t.teamId)")
    List<MemoryItem> findAccessibleToAgent(@Param("agentId") String agentId);
}
