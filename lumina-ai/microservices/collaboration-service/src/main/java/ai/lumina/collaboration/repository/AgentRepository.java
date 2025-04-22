package ai.lumina.collaboration.repository;

import ai.lumina.collaboration.model.Agent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Set;

/**
 * Repository interface for Agent entity operations.
 */
@Repository
public interface AgentRepository extends JpaRepository<Agent, String> {

    /**
     * Find agents by availability status.
     *
     * @param available The availability status to search for
     * @return List of agents with the specified availability
     */
    List<Agent> findByAvailable(boolean available);

    /**
     * Find agents by provider ID.
     *
     * @param providerId The provider ID to search for
     * @return List of agents from the specified provider
     */
    List<Agent> findByProviderId(String providerId);

    /**
     * Find agents by model ID.
     *
     * @param modelId The model ID to search for
     * @return List of agents with the specified model
     */
    List<Agent> findByModelId(String modelId);

    /**
     * Find agents with performance rating above a threshold.
     *
     * @param rating The minimum performance rating
     * @return List of agents with performance rating above the threshold
     */
    List<Agent> findByPerformanceRatingGreaterThanEqual(double rating);

    /**
     * Find agents with specific capabilities.
     *
     * @param capabilities The set of capabilities to search for
     * @return List of agents that have all the specified capabilities
     */
    @Query("SELECT a FROM Agent a JOIN a.capabilities c WHERE c IN :capabilities GROUP BY a HAVING COUNT(DISTINCT c) = :capabilityCount")
    List<Agent> findByCapabilities(@Param("capabilities") Set<String> capabilities, @Param("capabilityCount") long capabilityCount);

    /**
     * Find agents with at least one of the specified capabilities.
     *
     * @param capabilities The set of capabilities to search for
     * @return List of agents that have at least one of the specified capabilities
     */
    @Query("SELECT DISTINCT a FROM Agent a JOIN a.capabilities c WHERE c IN :capabilities")
    List<Agent> findByAnyCapability(@Param("capabilities") Set<String> capabilities);

    /**
     * Find available agents with specific capabilities and minimum performance rating.
     *
     * @param capabilities The set of capabilities to search for
     * @param rating The minimum performance rating
     * @return List of available agents with the specified capabilities and minimum rating
     */
    @Query("SELECT a FROM Agent a JOIN a.capabilities c WHERE a.available = true AND c IN :capabilities AND a.performanceRating >= :rating GROUP BY a HAVING COUNT(DISTINCT c) = :capabilityCount")
    List<Agent> findAvailableAgentsByCapabilitiesAndMinRating(
            @Param("capabilities") Set<String> capabilities,
            @Param("capabilityCount") long capabilityCount,
            @Param("rating") double rating);

    /**
     * Find top performing agents with specific capabilities.
     *
     * @param capabilities The set of capabilities to search for
     * @param limit The maximum number of agents to return
     * @return List of top performing agents with the specified capabilities
     */
    @Query("SELECT a FROM Agent a JOIN a.capabilities c WHERE c IN :capabilities GROUP BY a HAVING COUNT(DISTINCT c) = :capabilityCount ORDER BY a.performanceRating DESC")
    List<Agent> findTopPerformingAgentsByCapabilities(
            @Param("capabilities") Set<String> capabilities,
            @Param("capabilityCount") long capabilityCount,
            @Param("limit") int limit);
}
