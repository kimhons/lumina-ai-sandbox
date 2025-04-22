package ai.lumina.collaboration.repository;

import ai.lumina.collaboration.model.Team;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Set;

/**
 * Repository interface for Team entity operations.
 */
@Repository
public interface TeamRepository extends JpaRepository<Team, String> {

    /**
     * Find teams by status.
     *
     * @param status The status to search for
     * @return List of teams with the specified status
     */
    List<Team> findByStatus(String status);

    /**
     * Find teams with performance rating above a threshold.
     *
     * @param rating The minimum performance rating
     * @return List of teams with performance rating above the threshold
     */
    List<Team> findByPerformanceRatingGreaterThanEqual(double rating);

    /**
     * Find teams with specific capabilities.
     *
     * @param capabilities The set of capabilities to search for
     * @return List of teams that have all the specified capabilities
     */
    @Query("SELECT t FROM Team t JOIN t.capabilities c WHERE c IN :capabilities GROUP BY t HAVING COUNT(DISTINCT c) = :capabilityCount")
    List<Team> findByCapabilities(@Param("capabilities") Set<String> capabilities, @Param("capabilityCount") long capabilityCount);

    /**
     * Find teams with at least one of the specified capabilities.
     *
     * @param capabilities The set of capabilities to search for
     * @return List of teams that have at least one of the specified capabilities
     */
    @Query("SELECT DISTINCT t FROM Team t JOIN t.capabilities c WHERE c IN :capabilities")
    List<Team> findByAnyCapability(@Param("capabilities") Set<String> capabilities);

    /**
     * Find teams by leader.
     *
     * @param leaderId The ID of the leader agent
     * @return List of teams led by the specified agent
     */
    @Query("SELECT t FROM Team t WHERE t.leader.id = :leaderId")
    List<Team> findByLeaderId(@Param("leaderId") String leaderId);

    /**
     * Find teams containing a specific agent.
     *
     * @param agentId The ID of the agent
     * @return List of teams that include the specified agent
     */
    @Query("SELECT t FROM Team t JOIN t.agents a WHERE a.id = :agentId")
    List<Team> findByAgentId(@Param("agentId") String agentId);

    /**
     * Find teams with a specific size (number of agents).
     *
     * @param size The team size to search for
     * @return List of teams with the specified size
     */
    @Query("SELECT t FROM Team t WHERE SIZE(t.agents) = :size")
    List<Team> findByTeamSize(@Param("size") int size);

    /**
     * Find top performing teams with specific capabilities.
     *
     * @param capabilities The set of capabilities to search for
     * @param limit The maximum number of teams to return
     * @return List of top performing teams with the specified capabilities
     */
    @Query("SELECT t FROM Team t JOIN t.capabilities c WHERE c IN :capabilities GROUP BY t HAVING COUNT(DISTINCT c) = :capabilityCount ORDER BY t.performanceRating DESC")
    List<Team> findTopPerformingTeamsByCapabilities(
            @Param("capabilities") Set<String> capabilities,
            @Param("capabilityCount") long capabilityCount,
            @Param("limit") int limit);
}
