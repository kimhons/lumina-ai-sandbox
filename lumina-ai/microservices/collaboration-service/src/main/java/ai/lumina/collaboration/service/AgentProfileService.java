package ai.lumina.collaboration.service;

import ai.lumina.collaboration.model.AgentProfile;
import ai.lumina.collaboration.repository.AgentProfileRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Service for managing agent profiles in the collaboration system.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AgentProfileService {

    private final AgentProfileRepository agentProfileRepository;

    /**
     * Register a new agent in the collaboration system.
     *
     * @param agentId the agent ID
     * @param name the agent name
     * @param capabilities map of capabilities to their levels
     * @param specializations set of specializations
     * @param providerId optional provider ID
     * @param description optional description
     * @return the created agent profile
     */
    @Transactional
    public AgentProfile registerAgent(
            String agentId,
            String name,
            Map<String, Float> capabilities,
            Set<String> specializations,
            String providerId,
            String description) {
        
        log.info("Registering agent: {}", agentId);
        
        // Check if agent already exists
        Optional<AgentProfile> existingAgent = agentProfileRepository.findByAgentId(agentId);
        if (existingAgent.isPresent()) {
            log.info("Agent already exists, updating: {}", agentId);
            AgentProfile agent = existingAgent.get();
            agent.setName(name);
            agent.setCapabilities(capabilities);
            agent.setSpecializations(specializations);
            agent.setProviderId(providerId);
            agent.setDescription(description);
            agent.setActive(true);
            return agentProfileRepository.save(agent);
        }
        
        // Create new agent profile
        AgentProfile agent = AgentProfile.builder()
                .agentId(agentId)
                .name(name)
                .capabilities(capabilities)
                .specializations(specializations)
                .providerId(providerId)
                .description(description)
                .active(true)
                .build();
        
        return agentProfileRepository.save(agent);
    }

    /**
     * Get an agent profile by ID.
     *
     * @param agentId the agent ID
     * @return the agent profile, or empty if not found
     */
    @Transactional(readOnly = true)
    public Optional<AgentProfile> getAgent(String agentId) {
        return agentProfileRepository.findByAgentId(agentId);
    }

    /**
     * Get all active agents.
     *
     * @return list of active agent profiles
     */
    @Transactional(readOnly = true)
    public List<AgentProfile> getAllActiveAgents() {
        return agentProfileRepository.findByActiveTrue();
    }

    /**
     * Update an agent's capabilities.
     *
     * @param agentId the agent ID
     * @param capabilities the new capabilities map
     * @return the updated agent profile, or empty if agent not found
     */
    @Transactional
    public Optional<AgentProfile> updateCapabilities(String agentId, Map<String, Float> capabilities) {
        Optional<AgentProfile> agentOpt = agentProfileRepository.findByAgentId(agentId);
        if (agentOpt.isPresent()) {
            AgentProfile agent = agentOpt.get();
            agent.setCapabilities(capabilities);
            return Optional.of(agentProfileRepository.save(agent));
        }
        return Optional.empty();
    }

    /**
     * Update an agent's specializations.
     *
     * @param agentId the agent ID
     * @param specializations the new specializations set
     * @return the updated agent profile, or empty if agent not found
     */
    @Transactional
    public Optional<AgentProfile> updateSpecializations(String agentId, Set<String> specializations) {
        Optional<AgentProfile> agentOpt = agentProfileRepository.findByAgentId(agentId);
        if (agentOpt.isPresent()) {
            AgentProfile agent = agentOpt.get();
            agent.setSpecializations(specializations);
            return Optional.of(agentProfileRepository.save(agent));
        }
        return Optional.empty();
    }

    /**
     * Deactivate an agent.
     *
     * @param agentId the agent ID
     * @return true if agent was deactivated, false if agent not found
     */
    @Transactional
    public boolean deactivateAgent(String agentId) {
        Optional<AgentProfile> agentOpt = agentProfileRepository.findByAgentId(agentId);
        if (agentOpt.isPresent()) {
            AgentProfile agent = agentOpt.get();
            agent.setActive(false);
            agentProfileRepository.save(agent);
            log.info("Deactivated agent: {}", agentId);
            return true;
        }
        return false;
    }

    /**
     * Find agents with a specific capability.
     *
     * @param capability the capability name
     * @param minLevel the minimum capability level (optional)
     * @return list of matching agent profiles
     */
    @Transactional(readOnly = true)
    public List<AgentProfile> findAgentsByCapability(String capability, Float minLevel) {
        if (minLevel != null) {
            return agentProfileRepository.findByCapabilityWithMinLevel(capability, minLevel);
        } else {
            return agentProfileRepository.findByCapability(capability);
        }
    }

    /**
     * Find agents with a specific specialization.
     *
     * @param specialization the specialization
     * @return list of matching agent profiles
     */
    @Transactional(readOnly = true)
    public List<AgentProfile> findAgentsBySpecialization(String specialization) {
        return agentProfileRepository.findBySpecialization(specialization);
    }

    /**
     * Find agents that have all the specified capabilities.
     *
     * @param capabilities the set of required capabilities
     * @return list of matching agent profiles
     */
    @Transactional(readOnly = true)
    public List<AgentProfile> findAgentsByAllCapabilities(Set<String> capabilities) {
        if (capabilities.isEmpty()) {
            return Collections.emptyList();
        }
        return agentProfileRepository.findByAllCapabilities(capabilities, capabilities.size());
    }

    /**
     * Find agents by provider ID.
     *
     * @param providerId the provider ID
     * @return list of matching agent profiles
     */
    @Transactional(readOnly = true)
    public List<AgentProfile> findAgentsByProvider(String providerId) {
        return agentProfileRepository.findByProviderId(providerId);
    }

    /**
     * Get the capability level of an agent for a specific capability.
     *
     * @param agentId the agent ID
     * @param capability the capability name
     * @return the capability level, or 0.0 if not found
     */
    @Transactional(readOnly = true)
    public float getAgentCapabilityLevel(String agentId, String capability) {
        Optional<AgentProfile> agentOpt = agentProfileRepository.findByAgentId(agentId);
        if (agentOpt.isPresent()) {
            Map<String, Float> capabilities = agentOpt.get().getCapabilities();
            return capabilities.getOrDefault(capability, 0.0f);
        }
        return 0.0f;
    }

    /**
     * Check if an agent has a specific specialization.
     *
     * @param agentId the agent ID
     * @param specialization the specialization
     * @return true if the agent has the specialization, false otherwise
     */
    @Transactional(readOnly = true)
    public boolean hasAgentSpecialization(String agentId, String specialization) {
        Optional<AgentProfile> agentOpt = agentProfileRepository.findByAgentId(agentId);
        if (agentOpt.isPresent()) {
            Set<String> specializations = agentOpt.get().getSpecializations();
            return specializations.contains(specialization);
        }
        return false;
    }
}
