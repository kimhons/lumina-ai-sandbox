package ai.lumina.collaboration.repository;

import ai.lumina.collaboration.model.AgentProfile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.Set;

/**
 * Repository for managing AgentProfile entities.
 */
@Repository
public interface AgentProfileRepository extends JpaRepository<AgentProfile, String> {

    /**
     * Find an agent profile by agent ID.
     *
     * @param agentId the agent ID
     * @return the agent profile
     */
    Optional<AgentProfile> findByAgentId(String agentId);

    /**
     * Find all active agent profiles.
     *
     * @return list of active agent profiles
     */
    List<AgentProfile> findByActiveTrue();

    /**
     * Find agent profiles by provider ID.
     *
     * @param providerId the provider ID
     * @return list of agent profiles
     */
    List<AgentProfile> findByProviderId(String providerId);

    /**
     * Find agent profiles that have a specific capability.
     *
     * @param capability the capability name
     * @return list of agent profiles
     */
    @Query("SELECT ap FROM AgentProfile ap JOIN ap.capabilities c WHERE KEY(c) = :capability")
    List<AgentProfile> findByCapability(@Param("capability") String capability);

    /**
     * Find agent profiles that have a specific capability with a minimum level.
     *
     * @param capability the capability name
     * @param minLevel the minimum capability level
     * @return list of agent profiles
     */
    @Query("SELECT ap FROM AgentProfile ap JOIN ap.capabilities c WHERE KEY(c) = :capability AND VALUE(c) >= :minLevel")
    List<AgentProfile> findByCapabilityWithMinLevel(
            @Param("capability") String capability,
            @Param("minLevel") Float minLevel);

    /**
     * Find agent profiles that have a specific specialization.
     *
     * @param specialization the specialization
     * @return list of agent profiles
     */
    @Query("SELECT ap FROM AgentProfile ap JOIN ap.specializations s WHERE s = :specialization")
    List<AgentProfile> findBySpecialization(@Param("specialization") String specialization);

    /**
     * Find agent profiles that have all the specified capabilities.
     *
     * @param capabilities the set of capabilities
     * @return list of agent profiles
     */
    @Query("SELECT ap FROM AgentProfile ap WHERE " +
           "(SELECT COUNT(DISTINCT KEY(c)) FROM AgentProfile ap2 JOIN ap2.capabilities c " +
           "WHERE ap2 = ap AND KEY(c) IN :capabilities) = :capabilityCount")
    List<AgentProfile> findByAllCapabilities(
            @Param("capabilities") Set<String> capabilities,
            @Param("capabilityCount") long capabilityCount);
}
