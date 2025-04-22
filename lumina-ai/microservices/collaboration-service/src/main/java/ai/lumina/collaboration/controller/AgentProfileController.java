package ai.lumina.collaboration.controller;

import ai.lumina.collaboration.model.AgentProfile;
import ai.lumina.collaboration.service.AgentProfileService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * REST controller for managing agent profiles in the collaboration system.
 */
@RestController
@RequestMapping("/api/v1/collaboration/agents")
@RequiredArgsConstructor
@Slf4j
public class AgentProfileController {

    private final AgentProfileService agentProfileService;

    /**
     * Register a new agent.
     *
     * @param request the agent registration request
     * @return the created agent profile
     */
    @PostMapping
    public ResponseEntity<AgentProfile> registerAgent(@RequestBody AgentRegistrationRequest request) {
        log.info("Received request to register agent: {}", request.getAgentId());
        
        AgentProfile agent = agentProfileService.registerAgent(
                request.getAgentId(),
                request.getName(),
                request.getCapabilities(),
                request.getSpecializations(),
                request.getProviderId(),
                request.getDescription()
        );
        
        return ResponseEntity.status(HttpStatus.CREATED).body(agent);
    }

    /**
     * Get an agent by ID.
     *
     * @param agentId the agent ID
     * @return the agent profile, or 404 if not found
     */
    @GetMapping("/{agentId}")
    public ResponseEntity<AgentProfile> getAgent(@PathVariable String agentId) {
        log.info("Received request to get agent: {}", agentId);
        
        return agentProfileService.getAgent(agentId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get all active agents.
     *
     * @return list of active agent profiles
     */
    @GetMapping
    public ResponseEntity<List<AgentProfile>> getAllActiveAgents() {
        log.info("Received request to get all active agents");
        
        List<AgentProfile> agents = agentProfileService.getAllActiveAgents();
        return ResponseEntity.ok(agents);
    }

    /**
     * Update an agent's capabilities.
     *
     * @param agentId the agent ID
     * @param capabilities the new capabilities map
     * @return the updated agent profile, or 404 if not found
     */
    @PutMapping("/{agentId}/capabilities")
    public ResponseEntity<AgentProfile> updateCapabilities(
            @PathVariable String agentId,
            @RequestBody Map<String, Float> capabilities) {
        
        log.info("Received request to update capabilities for agent: {}", agentId);
        
        return agentProfileService.updateCapabilities(agentId, capabilities)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Update an agent's specializations.
     *
     * @param agentId the agent ID
     * @param specializations the new specializations set
     * @return the updated agent profile, or 404 if not found
     */
    @PutMapping("/{agentId}/specializations")
    public ResponseEntity<AgentProfile> updateSpecializations(
            @PathVariable String agentId,
            @RequestBody Set<String> specializations) {
        
        log.info("Received request to update specializations for agent: {}", agentId);
        
        return agentProfileService.updateSpecializations(agentId, specializations)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Deactivate an agent.
     *
     * @param agentId the agent ID
     * @return 204 if successful, 404 if agent not found
     */
    @DeleteMapping("/{agentId}")
    public ResponseEntity<Void> deactivateAgent(@PathVariable String agentId) {
        log.info("Received request to deactivate agent: {}", agentId);
        
        boolean success = agentProfileService.deactivateAgent(agentId);
        return success ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }

    /**
     * Find agents by capability.
     *
     * @param capability the capability name
     * @param minLevel optional minimum capability level
     * @return list of matching agent profiles
     */
    @GetMapping("/search/by-capability")
    public ResponseEntity<List<AgentProfile>> findAgentsByCapability(
            @RequestParam String capability,
            @RequestParam(required = false) Float minLevel) {
        
        log.info("Received request to find agents by capability: {}, minLevel: {}", capability, minLevel);
        
        List<AgentProfile> agents = agentProfileService.findAgentsByCapability(capability, minLevel);
        return ResponseEntity.ok(agents);
    }

    /**
     * Find agents by specialization.
     *
     * @param specialization the specialization
     * @return list of matching agent profiles
     */
    @GetMapping("/search/by-specialization")
    public ResponseEntity<List<AgentProfile>> findAgentsBySpecialization(
            @RequestParam String specialization) {
        
        log.info("Received request to find agents by specialization: {}", specialization);
        
        List<AgentProfile> agents = agentProfileService.findAgentsBySpecialization(specialization);
        return ResponseEntity.ok(agents);
    }

    /**
     * Find agents by provider.
     *
     * @param providerId the provider ID
     * @return list of matching agent profiles
     */
    @GetMapping("/search/by-provider")
    public ResponseEntity<List<AgentProfile>> findAgentsByProvider(
            @RequestParam String providerId) {
        
        log.info("Received request to find agents by provider: {}", providerId);
        
        List<AgentProfile> agents = agentProfileService.findAgentsByProvider(providerId);
        return ResponseEntity.ok(agents);
    }

    /**
     * Agent registration request.
     */
    public static class AgentRegistrationRequest {
        private String agentId;
        private String name;
        private Map<String, Float> capabilities;
        private Set<String> specializations;
        private String providerId;
        private String description;

        // Getters and setters
        public String getAgentId() { return agentId; }
        public void setAgentId(String agentId) { this.agentId = agentId; }
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public Map<String, Float> getCapabilities() { return capabilities; }
        public void setCapabilities(Map<String, Float> capabilities) { this.capabilities = capabilities; }
        
        public Set<String> getSpecializations() { return specializations; }
        public void setSpecializations(Set<String> specializations) { this.specializations = specializations; }
        
        public String getProviderId() { return providerId; }
        public void setProviderId(String providerId) { this.providerId = providerId; }
        
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
    }
}
