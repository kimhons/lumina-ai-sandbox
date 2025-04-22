package ai.lumina.collaboration.repository;

import ai.lumina.collaboration.model.AgentTeam;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository for managing AgentTeam entities.
 */
@Repository
public interface AgentTeamRepository extends JpaRepository<AgentTeam, String> {

    /**
     * Find a team by team ID.
     *
     * @param teamId the team ID
     * @return the agent team
     */
    Optional<AgentTeam> findByTeamId(String teamId);

    /**
     * Find teams by task ID.
     *
     * @param taskId the task ID
     * @return list of agent teams
     */
    List<AgentTeam> findByTaskId(String taskId);

    /**
     * Find teams by status.
     *
     * @param status the team status
     * @return list of agent teams
     */
    List<AgentTeam> findByStatus(AgentTeam.TeamStatus status);

    /**
     * Find teams by leader ID.
     *
     * @param leaderId the leader ID
     * @return list of agent teams
     */
    List<AgentTeam> findByLeaderId(String leaderId);

    /**
     * Find teams that have a specific agent as a member.
     *
     * @param agentId the agent ID
     * @return list of agent teams
     */
    @Query("SELECT t FROM AgentTeam t JOIN t.members m WHERE m = :agentId")
    List<AgentTeam> findByMember(@Param("agentId") String agentId);

    /**
     * Find teams that were formed using a specific strategy.
     *
     * @param strategy the formation strategy
     * @return list of agent teams
     */
    List<AgentTeam> findByFormationStrategy(String strategy);

    /**
     * Find teams with a performance score above a threshold.
     *
     * @param minScore the minimum performance score
     * @return list of agent teams
     */
    List<AgentTeam> findByPerformanceScoreGreaterThanEqual(Float minScore);

    /**
     * Find teams that have a specific agent in a specific role.
     *
     * @param agentId the agent ID
     * @param role the role name
     * @return list of agent teams
     */
    @Query("SELECT t FROM AgentTeam t JOIN t.roles r WHERE KEY(r) = :agentId AND EXISTS (SELECT 1 FROM MAP_KEYS(VALUE(r)) k WHERE k = :role)")
    List<AgentTeam> findByAgentRole(@Param("agentId") String agentId, @Param("role") String role);
}
