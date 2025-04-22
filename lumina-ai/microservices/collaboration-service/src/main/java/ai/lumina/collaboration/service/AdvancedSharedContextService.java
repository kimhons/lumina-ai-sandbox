package ai.lumina.collaboration.service;

import ai.lumina.collaboration.model.*;
import ai.lumina.collaboration.repository.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

/**
 * Enhanced service for managing shared context between agents in a collaborative environment.
 * This service provides advanced context synchronization, memory integration, and versioning capabilities.
 */
@Service
public class AdvancedSharedContextService {

    private static final Logger logger = LoggerFactory.getLogger(AdvancedSharedContextService.class);

    @Autowired
    private SharedContextRepository sharedContextRepository;

    @Autowired
    private AgentRepository agentRepository;

    @Autowired
    private TeamRepository teamRepository;

    @Value("${collaboration.shared-context.sync-interval-ms:500}")
    private long syncIntervalMs;

    @Value("${collaboration.shared-context.max-size-mb:200}")
    private long maxSizeMb;

    @Value("${collaboration.memory.service-url:http://memory-service:8086}")
    private String memoryServiceUrl;

    @Value("${collaboration.memory.context-compression-threshold:5000}")
    private int compressionThreshold;

    @Autowired
    private RestTemplate restTemplate;

    /**
     * Creates a new shared context for a team.
     *
     * @param team The team for which to create a shared context
     * @return The created shared context
     */
    @Transactional
    public SharedContext createSharedContext(Team team) {
        logger.info("Creating shared context for team: {}", team.getName());
        
        SharedContext context = new SharedContext();
        context.setName("Context for " + team.getName());
        context.setTeam(team);
        context.setCreatedAt(LocalDateTime.now());
        context.setLastUpdatedAt(LocalDateTime.now());
        context.setVersion(1L);
        context.setData(new HashMap<>());
        context.setAccessControl(new HashMap<>());
        
        // Set up initial access control for all team members
        for (Agent agent : team.getAgents()) {
            Set<String> permissions = new HashSet<>();
            permissions.add("READ");
            permissions.add("WRITE");
            context.getAccessControl().put(agent.getId(), permissions);
        }
        
        return sharedContextRepository.save(context);
    }
    
    /**
     * Updates a value in the shared context with versioning support.
     *
     * @param contextId The ID of the shared context
     * @param agentId The ID of the agent making the update
     * @param key The key to update
     * @param value The new value
     * @return The updated shared context
     */
    @Transactional
    public SharedContext updateContextValue(String contextId, String agentId, String key, Object value) {
        SharedContext context = sharedContextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Shared context not found with ID: " + contextId));
        
        // Check access control
        if (!hasWriteAccess(context, agentId)) {
            throw new SecurityException("Agent does not have write access to this context");
        }
        
        // Create a new version if the key already exists
        if (context.getData().containsKey(key)) {
            context.setVersion(context.getVersion() + 1);
            
            // Archive previous version if needed
            if (shouldArchiveVersion(context)) {
                archiveContextVersion(context);
            }
        }
        
        // Update the value
        context.getData().put(key, value);
        context.setLastUpdatedAt(LocalDateTime.now());
        context.getLastUpdatedBy().put(key, agentId);
        
        // Check if context size exceeds threshold for compression
        if (estimateContextSize(context) > compressionThreshold) {
            compressContext(context);
        }
        
        return sharedContextRepository.save(context);
    }
    
    /**
     * Retrieves a value from the shared context.
     *
     * @param contextId The ID of the shared context
     * @param agentId The ID of the agent making the request
     * @param key The key to retrieve
     * @return The value associated with the key
     */
    @Cacheable(value = "sharedContexts", key = "#contextId + '-' + #key")
    public Object getContextValue(String contextId, String agentId, String key) {
        SharedContext context = sharedContextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Shared context not found with ID: " + contextId));
        
        // Check access control
        if (!hasReadAccess(context, agentId)) {
            throw new SecurityException("Agent does not have read access to this context");
        }
        
        return context.getData().get(key);
    }
    
    /**
     * Synchronizes the shared context with all team members.
     *
     * @param contextId The ID of the shared context to synchronize
     */
    @Async("collaborationTaskExecutor")
    public CompletableFuture<Void> synchronizeContext(String contextId) {
        SharedContext context = sharedContextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Shared context not found with ID: " + contextId));
        
        Team team = context.getTeam();
        if (team == null) {
            logger.warn("Cannot synchronize context without associated team");
            return CompletableFuture.completedFuture(null);
        }
        
        logger.info("Synchronizing context for team: {}", team.getName());
        
        // Notify all team members about context update
        for (Agent agent : team.getAgents()) {
            if (hasReadAccess(context, agent.getId())) {
                notifyAgentOfContextUpdate(agent.getId(), contextId);
            }
        }
        
        return CompletableFuture.completedFuture(null);
    }
    
    /**
     * Integrates the shared context with the memory system for long-term storage.
     *
     * @param contextId The ID of the shared context to integrate
     * @return True if integration was successful, false otherwise
     */
    @Transactional
    public boolean integrateWithMemory(String contextId) {
        SharedContext context = sharedContextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Shared context not found with ID: " + contextId));
        
        try {
            // Prepare memory integration payload
            Map<String, Object> memoryPayload = new HashMap<>();
            memoryPayload.put("contextId", context.getId());
            memoryPayload.put("teamId", context.getTeam().getId());
            memoryPayload.put("data", context.getData());
            memoryPayload.put("version", context.getVersion());
            memoryPayload.put("timestamp", context.getLastUpdatedAt());
            
            // Send to memory service
            String memoryEndpoint = memoryServiceUrl + "/api/v1/memory/context";
            restTemplate.postForEntity(memoryEndpoint, memoryPayload, Map.class);
            
            logger.info("Successfully integrated context {} with memory system", contextId);
            return true;
        } catch (Exception e) {
            logger.error("Failed to integrate context with memory system", e);
            return false;
        }
    }
    
    /**
     * Checks if an agent has read access to a shared context.
     *
     * @param context The shared context
     * @param agentId The ID of the agent
     * @return True if the agent has read access, false otherwise
     */
    private boolean hasReadAccess(SharedContext context, String agentId) {
        Set<String> permissions = context.getAccessControl().get(agentId);
        return permissions != null && permissions.contains("READ");
    }
    
    /**
     * Checks if an agent has write access to a shared context.
     *
     * @param context The shared context
     * @param agentId The ID of the agent
     * @return True if the agent has write access, false otherwise
     */
    private boolean hasWriteAccess(SharedContext context, String agentId) {
        Set<String> permissions = context.getAccessControl().get(agentId);
        return permissions != null && permissions.contains("WRITE");
    }
    
    /**
     * Notifies an agent about a context update.
     *
     * @param agentId The ID of the agent to notify
     * @param contextId The ID of the updated context
     */
    private void notifyAgentOfContextUpdate(String agentId, String contextId) {
        // In a real implementation, this would use a messaging system to notify agents
        logger.info("Notifying agent {} about context update {}", agentId, contextId);
    }
    
    /**
     * Determines if a context version should be archived based on change frequency and importance.
     *
     * @param context The shared context
     * @return True if the version should be archived, false otherwise
     */
    private boolean shouldArchiveVersion(SharedContext context) {
        // Archive every 5 versions or if the context is marked as important
        return context.getVersion() % 5 == 0 || Boolean.TRUE.equals(context.getIsImportant());
    }
    
    /**
     * Archives a version of the shared context to the memory system.
     *
     * @param context The shared context to archive
     */
    private void archiveContextVersion(SharedContext context) {
        try {
            // Prepare archive payload
            Map<String, Object> archivePayload = new HashMap<>();
            archivePayload.put("contextId", context.getId());
            archivePayload.put("version", context.getVersion());
            archivePayload.put("data", context.getData());
            archivePayload.put("timestamp", context.getLastUpdatedAt());
            
            // Send to memory service for archiving
            String archiveEndpoint = memoryServiceUrl + "/api/v1/memory/archive";
            restTemplate.postForEntity(archiveEndpoint, archivePayload, Map.class);
            
            logger.info("Archived version {} of context {}", context.getVersion(), context.getId());
        } catch (Exception e) {
            logger.error("Failed to archive context version", e);
        }
    }
    
    /**
     * Estimates the size of a shared context in bytes.
     *
     * @param context The shared context
     * @return The estimated size in bytes
     */
    private long estimateContextSize(SharedContext context) {
        // This is a simplified estimation
        return context.getData().toString().length() * 2; // Rough estimate: 2 bytes per character
    }
    
    /**
     * Compresses a shared context by sending it to the memory service for compression.
     *
     * @param context The shared context to compress
     */
    private void compressContext(SharedContext context) {
        try {
            // Prepare compression payload
            Map<String, Object> compressionPayload = new HashMap<>();
            compressionPayload.put("contextId", context.getId());
            compressionPayload.put("data", context.getData());
            
            // Send to memory service for compression
            String compressionEndpoint = memoryServiceUrl + "/api/v1/memory/compress";
            Map<String, Object> compressedData = restTemplate.postForObject(
                    compressionEndpoint, compressionPayload, Map.class);
            
            if (compressedData != null && compressedData.containsKey("compressedData")) {
                // Update context with compressed data
                context.setData((Map<String, Object>) compressedData.get("compressedData"));
                context.setIsCompressed(true);
                logger.info("Successfully compressed context {}", context.getId());
            }
        } catch (Exception e) {
            logger.error("Failed to compress context", e);
        }
    }
    
    /**
     * Retrieves a specific version of a shared context from the archive.
     *
     * @param contextId The ID of the shared context
     * @param version The version to retrieve
     * @return The archived context version
     */
    public Map<String, Object> getArchivedVersion(String contextId, Long version) {
        try {
            String archiveEndpoint = memoryServiceUrl + "/api/v1/memory/archive/" + contextId + "/" + version;
            return restTemplate.getForObject(archiveEndpoint, Map.class);
        } catch (Exception e) {
            logger.error("Failed to retrieve archived context version", e);
            return null;
        }
    }
    
    /**
     * Merges multiple shared contexts into a single unified context.
     *
     * @param contextIds The IDs of the contexts to merge
     * @param teamId The ID of the team that will own the merged context
     * @return The merged shared context
     */
    @Transactional
    public SharedContext mergeContexts(List<String> contextIds, String teamId) {
        if (contextIds.size() < 2) {
            throw new IllegalArgumentException("At least two contexts are required for merging");
        }
        
        Team team = teamRepository.findById(teamId)
                .orElseThrow(() -> new NoSuchElementException("Team not found with ID: " + teamId));
        
        // Create a new context for the merged result
        SharedContext mergedContext = new SharedContext();
        mergedContext.setName("Merged Context for " + team.getName());
        mergedContext.setTeam(team);
        mergedContext.setCreatedAt(LocalDateTime.now());
        mergedContext.setLastUpdatedAt(LocalDateTime.now());
        mergedContext.setVersion(1L);
        mergedContext.setData(new HashMap<>());
        mergedContext.setAccessControl(new HashMap<>());
        
        // Set up access control for all team members
        for (Agent agent : team.getAgents()) {
            Set<String> permissions = new HashSet<>();
            permissions.add("READ");
            permissions.add("WRITE");
            mergedContext.getAccessControl().put(agent.getId(), permissions);
        }
        
        // Merge data from all contexts
        for (String contextId : contextIds) {
            SharedContext context = sharedContextRepository.findById(contextId)
                    .orElseThrow(() -> new NoSuchElementException("Shared context not found with ID: " + contextId));
            
            // Merge data, handling conflicts by keeping the most recent value
            for (Map.Entry<String, Object> entry : context.getData().entrySet()) {
                String key = entry.getKey();
                Object value = entry.getValue();
                
                if (!mergedContext.getData().containsKey(key) || 
                    context.getLastUpdatedAt().isAfter(mergedContext.getLastUpdatedAt())) {
                    mergedContext.getData().put(key, value);
                    if (context.getLastUpdatedBy().containsKey(key)) {
                        mergedContext.getLastUpdatedBy().put(key, context.getLastUpdatedBy().get(key));
                    }
                }
            }
        }
        
        return sharedContextRepository.save(mergedContext);
    }
}
