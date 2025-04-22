package ai.lumina.collaboration.repository;

import ai.lumina.collaboration.model.Role;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Set;

/**
 * Repository interface for Role entity operations.
 */
@Repository
public interface RoleRepository extends JpaRepository<Role, String> {

    /**
     * Find roles by team ID.
     *
     * @param teamId The team ID to search for
     * @return List of roles associated with the specified team
     */
    @Query("SELECT r FROM Role r WHERE r.team.id = :teamId")
    List<Role> findByTeamId(@Param("teamId") String teamId);

    /**
     * Find roles by assigned agent ID.
     *
     * @param agentId The agent ID to search for
     * @return List of roles assigned to the specified agent
     */
    @Query("SELECT r FROM Role r WHERE r.assignedAgent.id = :agentId")
    List<Role> findByAssignedAgentId(@Param("agentId") String agentId);

    /**
     * Find roles by filled status.
     *
     * @param filled The filled status to search for
     * @return List of roles with the specified filled status
     */
    List<Role> findByFilled(boolean filled);

    /**
     * Find unfilled roles by team ID.
     *
     * @param teamId The team ID to search for
     * @return List of unfilled roles for the specified team
     */
    @Query("SELECT r FROM Role r WHERE r.team.id = :teamId AND r.filled = false")
    List<Role> findUnfilledRolesByTeamId(@Param("teamId") String teamId);

    /**
     * Find roles by priority.
     *
     * @param priority The priority level to search for
     * @return List of roles with the specified priority
     */
    List<Role> findByPriority(int priority);

    /**
     * Find roles by priority greater than or equal to a threshold.
     *
     * @param priority The minimum priority level
     * @return List of roles with priority greater than or equal to the threshold
     */
    List<Role> findByPriorityGreaterThanEqual(int priority);

    /**
     * Find roles requiring specific capabilities.
     *
     * @param capabilities The set of capabilities to search for
     * @return List of roles that require all the specified capabilities
     */
    @Query("SELECT r FROM Role r JOIN r.requiredCapabilities c WHERE c IN :capabilities GROUP BY r HAVING COUNT(DISTINCT c) = :capabilityCount")
    List<Role> findByRequiredCapabilities(@Param("capabilities") Set<String> capabilities, @Param("capabilityCount") long capabilityCount);

    /**
     * Find roles requiring at least one of the specified capabilities.
     *
     * @param capabilities The set of capabilities to search for
     * @return List of roles that require at least one of the specified capabilities
     */
    @Query("SELECT DISTINCT r FROM Role r JOIN r.requiredCapabilities c WHERE c IN :capabilities")
    List<Role> findByAnyRequiredCapability(@Param("capabilities") Set<String> capabilities);

    /**
     * Find high-priority unfilled roles.
     *
     * @param minPriority The minimum priority level
     * @return List of unfilled roles with priority greater than or equal to the threshold
     */
    @Query("SELECT r FROM Role r WHERE r.filled = false AND r.priority >= :minPriority ORDER BY r.priority DESC")
    List<Role> findHighPriorityUnfilledRoles(@Param("minPriority") int minPriority);
}
