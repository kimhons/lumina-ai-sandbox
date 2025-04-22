package ai.lumina.collaboration.service;

import ai.lumina.collaboration.model.*;
import ai.lumina.collaboration.repository.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Enhanced service for shared context management operations.
 */
@Service
public class SharedContextService {

    private static final Logger logger = LoggerFactory.getLogger(SharedContextService.class);

    @Autowired
    private SharedContextRepository contextRepository;

    @Autowired
    private ContextVersionRepository versionRepository;

    @Autowired
    private ContextAccessRepository accessRepository;

    @Autowired
    private AgentRepository agentRepository;

    @Value("${collaboration.context.memory-integration-enabled:true}")
    private boolean memoryIntegrationEnabled;

    @Autowired(required = false)
    private MemoryIntegrationService memoryService;

    /**
     * Create a new shared context.
     *
     * @param name Name of the context
     * @param contextType Type of the context
     * @param ownerId ID of the agent creating the context
     * @param initialContent Initial content of the context
     * @param accessControl Initial access control settings
     * @return The created shared context
     */
    @Transactional
    public SharedContext createContext(
            String name,
            String contextType,
            String ownerId,
            Map<String, Object> initialContent,
            List<Map<String, Object>> accessControl) {
        
        logger.info("Creating shared context: {} of type {} for owner: {}", name, contextType, ownerId);
        
        // Create initial version
        ContextVersion initialVersion = new ContextVersion();
        initialVersion.setVersionId(UUID.randomUUID().toString());
        initialVersion.setTimestamp(LocalDateTime.now());
        initialVersion.setAgentId(ownerId);
        initialVersion.setChanges(Collections.singletonList(
                new ContextChange(
                        ownerId,
                        LocalDateTime.now(),
                        "CREATE",
                        "/",
                        null,
                        initialContent,
                        new HashMap<>()
                )
        ));
        initialVersion.computeHash();
        
        // Create context
        SharedContext context = new SharedContext();
        context.setId(UUID.randomUUID().toString());
        context.setName(name);
        context.setContextType(contextType);
        context.setOwnerId(ownerId);
        context.setCreatedAt(LocalDateTime.now());
        context.setUpdatedAt(LocalDateTime.now());
        context.setContent(initialContent != null ? initialContent : new HashMap<>());
        context.setCurrentVersionId(initialVersion.getVersionId());
        context.setSubscribers(new HashSet<>(Collections.singletonList(ownerId)));
        
        // Save version
        versionRepository.save(initialVersion);
        
        // Process access control
        if (accessControl != null) {
            for (Map<String, Object> access : accessControl) {
                String agentId = (String) access.get("agentId");
                String accessLevel = (String) access.get("accessLevel");
                Double expiresIn = access.get("expiresIn") != null ? 
                        ((Number) access.get("expiresIn")).doubleValue() : null;
                
                ContextAccess contextAccess = new ContextAccess();
                contextAccess.setAgentId(agentId);
                contextAccess.setAccessLevel(accessLevel);
                contextAccess.setGrantedAt(LocalDateTime.now());
                contextAccess.setGrantedBy(ownerId);
                
                if (expiresIn != null) {
                    contextAccess.setExpiresAt(LocalDateTime.now().plusSeconds(expiresIn.longValue()));
                }
                
                contextAccess.setContext(context);
                context.getAccessControl().add(contextAccess);
            }
        }
        
        // Save context
        SharedContext savedContext = contextRepository.save(context);
        
        // Integrate with memory system if enabled
        if (memoryIntegrationEnabled && memoryService != null) {
            memoryService.storeContextInMemory(savedContext);
        }
        
        return savedContext;
    }

    /**
     * Get a shared context by ID.
     *
     * @param contextId ID of the context
     * @param agentId ID of the agent requesting the context
     * @return The shared context
     * @throws NoSuchElementException if context not found
     * @throws SecurityException if agent does not have access
     */
    @Transactional(readOnly = true)
    public SharedContext getContext(String contextId, String agentId) {
        SharedContext context = contextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Context not found: " + contextId));
        
        // Check if agent can read
        if (!canAgentPerform(context, agentId, "READ")) {
            throw new SecurityException("Agent does not have read permission: " + agentId);
        }
        
        return context;
    }

    /**
     * Update a shared context.
     *
     * @param contextId ID of the context to update
     * @param agentId ID of the agent making the update
     * @param updates Dictionary of updates to apply (path -> value)
     * @param metadata Optional metadata for the update
     * @return The updated shared context
     * @throws NoSuchElementException if context not found
     * @throws SecurityException if agent does not have access
     */
    @Transactional
    public SharedContext updateContext(
            String contextId,
            String agentId,
            Map<String, Object> updates,
            Map<String, Object> metadata) {
        
        SharedContext context = contextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Context not found: " + contextId));
        
        // Check if agent can update
        if (!canAgentPerform(context, agentId, "UPDATE")) {
            throw new SecurityException("Agent does not have update permission: " + agentId);
        }
        
        // Create changes
        List<ContextChange> changes = new ArrayList<>();
        for (Map.Entry<String, Object> entry : updates.entrySet()) {
            String path = entry.getKey();
            Object newValue = entry.getValue();
            
            // Get old value
            Object oldValue = getValueAtPath(context.getContent(), path);
            
            // Create change
            ContextChange change = new ContextChange(
                    agentId,
                    LocalDateTime.now(),
                    "UPDATE",
                    path,
                    oldValue,
                    newValue,
                    metadata != null ? metadata : new HashMap<>()
            );
            changes.add(change);
            
            // Apply update
            setValueAtPath(context.getContent(), path, newValue);
        }
        
        // Create new version
        ContextVersion newVersion = new ContextVersion();
        newVersion.setVersionId(UUID.randomUUID().toString());
        newVersion.setTimestamp(LocalDateTime.now());
        newVersion.setAgentId(agentId);
        newVersion.setParentVersionId(context.getCurrentVersionId());
        newVersion.setChanges(changes);
        newVersion.setMetadata(metadata != null ? metadata : new HashMap<>());
        newVersion.computeHash();
        
        // Save version
        versionRepository.save(newVersion);
        
        // Update context
        context.setCurrentVersionId(newVersion.getVersionId());
        context.setUpdatedAt(LocalDateTime.now());
        
        // Save context
        SharedContext savedContext = contextRepository.save(context);
        
        // Notify subscribers
        notifySubscribers(context, changes);
        
        // Update in memory system if enabled
        if (memoryIntegrationEnabled && memoryService != null) {
            memoryService.updateContextInMemory(savedContext);
        }
        
        return savedContext;
    }

    /**
     * Merge two shared contexts.
     *
     * @param targetContextId ID of the target context
     * @param sourceContextId ID of the source context
     * @param agentId ID of the agent performing the merge
     * @param conflictResolution Strategy for resolving conflicts
     * @return The merged context
     * @throws NoSuchElementException if context not found
     * @throws SecurityException if agent does not have access
     */
    @Transactional
    public SharedContext mergeContexts(
            String targetContextId,
            String sourceContextId,
            String agentId,
            String conflictResolution) {
        
        SharedContext targetContext = contextRepository.findById(targetContextId)
                .orElseThrow(() -> new NoSuchElementException("Target context not found: " + targetContextId));
        
        SharedContext sourceContext = contextRepository.findById(sourceContextId)
                .orElseThrow(() -> new NoSuchElementException("Source context not found: " + sourceContextId));
        
        // Check if agent can update target and read source
        if (!canAgentPerform(targetContext, agentId, "UPDATE")) {
            throw new SecurityException("Agent does not have update permission for target context: " + agentId);
        }
        
        if (!canAgentPerform(sourceContext, agentId, "READ")) {
            throw new SecurityException("Agent does not have read permission for source context: " + agentId);
        }
        
        // Perform merge
        Map<String, Object> mergedContent = mergeContents(
                targetContext.getContent(),
                sourceContext.getContent(),
                conflictResolution != null ? conflictResolution : "latest"
        );
        
        // Create change
        ContextChange change = new ContextChange(
                agentId,
                LocalDateTime.now(),
                "MERGE",
                "/",
                targetContext.getContent(),
                mergedContent,
                Collections.singletonMap("sourceContextId", sourceContextId)
        );
        
        // Update target content
        targetContext.setContent(mergedContent);
        
        // Create new version
        ContextVersion newVersion = new ContextVersion();
        newVersion.setVersionId(UUID.randomUUID().toString());
        newVersion.setTimestamp(LocalDateTime.now());
        newVersion.setAgentId(agentId);
        newVersion.setParentVersionId(targetContext.getCurrentVersionId());
        newVersion.setChanges(Collections.singletonList(change));
        newVersion.setMetadata(Map.of(
                "mergeSource", sourceContextId,
                "conflictResolution", conflictResolution != null ? conflictResolution : "latest"
        ));
        newVersion.computeHash();
        
        // Save version
        versionRepository.save(newVersion);
        
        // Update context
        targetContext.setCurrentVersionId(newVersion.getVersionId());
        targetContext.setUpdatedAt(LocalDateTime.now());
        
        // Save context
        SharedContext savedContext = contextRepository.save(targetContext);
        
        // Notify subscribers
        notifySubscribers(targetContext, Collections.singletonList(change));
        
        // Update in memory system if enabled
        if (memoryIntegrationEnabled && memoryService != null) {
            memoryService.updateContextInMemory(savedContext);
        }
        
        return savedContext;
    }

    /**
     * Fork a shared context to create a new one.
     *
     * @param contextId ID of the context to fork
     * @param agentId ID of the agent performing the fork
     * @param newName Name for the new context
     * @return The new forked context
     * @throws NoSuchElementException if context not found
     * @throws SecurityException if agent does not have access
     */
    @Transactional
    public SharedContext forkContext(
            String contextId,
            String agentId,
            String newName) {
        
        SharedContext sourceContext = contextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Context not found: " + contextId));
        
        // Check if agent can read source
        if (!canAgentPerform(sourceContext, agentId, "READ")) {
            throw new SecurityException("Agent does not have read permission: " + agentId);
        }
        
        // Create new context with copy of content
        String actualNewName = newName != null ? newName : "Fork of " + sourceContext.getName();
        Map<String, Object> newContent = deepCopy(sourceContext.getContent());
        
        // Create new context
        SharedContext forkedContext = createContext(
                actualNewName,
                sourceContext.getContextType(),
                agentId,
                newContent,
                null  // Start with clean access control
        );
        
        // Add metadata about fork
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("forkedFrom", contextId);
        metadata.put("forkTime", LocalDateTime.now());
        forkedContext.setMetadata(metadata);
        
        // Save context
        SharedContext savedContext = contextRepository.save(forkedContext);
        
        // Update in memory system if enabled
        if (memoryIntegrationEnabled && memoryService != null) {
            memoryService.updateContextInMemory(savedContext);
        }
        
        return savedContext;
    }

    /**
     * Grant access to a shared context for an agent.
     *
     * @param contextId ID of the context
     * @param grantingAgentId ID of the agent granting access
     * @param targetAgentId ID of the agent receiving access
     * @param accessLevel Level of access to grant
     * @param expiresIn Optional time in seconds until access expires
     * @return True if access was granted, false otherwise
     * @throws NoSuchElementException if context not found
     * @throws SecurityException if agent does not have access
     */
    @Transactional
    public boolean grantAccess(
            String contextId,
            String grantingAgentId,
            String targetAgentId,
            String accessLevel,
            Double expiresIn) {
        
        SharedContext context = contextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Context not found: " + contextId));
        
        // Check if granting agent has admin access
        if (!canAgentPerform(context, grantingAgentId, "DELETE")) {  // DELETE requires ADMIN
            throw new SecurityException("Agent does not have admin permission: " + grantingAgentId);
        }
        
        // Calculate expiration time if provided
        LocalDateTime expiresAt = null;
        if (expiresIn != null) {
            expiresAt = LocalDateTime.now().plusSeconds(expiresIn.longValue());
        }
        
        // Find existing access
        ContextAccess existingAccess = null;
        for (ContextAccess access : context.getAccessControl()) {
            if (access.getAgentId().equals(targetAgentId)) {
                existingAccess = access;
                break;
            }
        }
        
        if (existingAccess != null) {
            // Update existing access
            existingAccess.setAccessLevel(accessLevel);
            existingAccess.setGrantedAt(LocalDateTime.now());
            existingAccess.setGrantedBy(grantingAgentId);
            existingAccess.setExpiresAt(expiresAt);
            accessRepository.save(existingAccess);
        } else {
            // Create new access
            ContextAccess newAccess = new ContextAccess();
            newAccess.setAgentId(targetAgentId);
            newAccess.setAccessLevel(accessLevel);
            newAccess.setGrantedAt(LocalDateTime.now());
            newAccess.setGrantedBy(grantingAgentId);
            newAccess.setExpiresAt(expiresAt);
            newAccess.setContext(context);
            
            context.getAccessControl().add(newAccess);
            accessRepository.save(newAccess);
        }
        
        // Update context
        contextRepository.save(context);
        
        // Update in memory system if enabled
        if (memoryIntegrationEnabled && memoryService != null) {
            memoryService.updateContextInMemory(context);
        }
        
        return true;
    }

    /**
     * Revoke access to a shared context for an agent.
     *
     * @param contextId ID of the context
     * @param revokingAgentId ID of the agent revoking access
     * @param targetAgentId ID of the agent whose access is being revoked
     * @return True if access was revoked, false otherwise
     * @throws NoSuchElementException if context not found
     * @throws SecurityException if agent does not have access
     */
    @Transactional
    public boolean revokeAccess(
            String contextId,
            String revokingAgentId,
            String targetAgentId) {
        
        SharedContext context = contextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Context not found: " + contextId));
        
        // Check if revoking agent has admin access
        if (!canAgentPerform(context, revokingAgentId, "DELETE")) {  // DELETE requires ADMIN
            throw new SecurityException("Agent does not have admin permission: " + revokingAgentId);
        }
        
        // Cannot revoke access for the owner
        if (targetAgentId.equals(context.getOwnerId())) {
            throw new IllegalArgumentException("Cannot revoke access for owner of context");
        }
        
        // Find and remove access
        ContextAccess accessToRemove = null;
        for (ContextAccess access : context.getAccessControl()) {
            if (access.getAgentId().equals(targetAgentId)) {
                accessToRemove = access;
                break;
            }
        }
        
        if (accessToRemove != null) {
            context.getAccessControl().remove(accessToRemove);
            accessRepository.delete(accessToRemove);
            
            // Update context
            contextRepository.save(context);
            
            // Update in memory system if enabled
            if (memoryIntegrationEnabled && memoryService != null) {
                memoryService.updateContextInMemory(context);
            }
            
            return true;
        }
        
        return false;
    }

    /**
     * Subscribe an agent to updates for a shared context.
     *
     * @param contextId ID of the context
     * @param agentId ID of the agent subscribing
     * @return True if subscription was successful, false otherwise
     * @throws NoSuchElementException if context not found
     * @throws SecurityException if agent does not have access
     */
    @Transactional
    public boolean subscribe(String contextId, String agentId) {
        SharedContext context = contextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Context not found: " + contextId));
        
        // Check if agent can read
        if (!canAgentPerform(context, agentId, "READ")) {
            throw new SecurityException("Agent does not have read permission: " + agentId);
        }
        
        // Add to subscribers
        if (!context.getSubscribers().contains(agentId)) {
            context.getSubscribers().add(agentId);
            
            // Update context
            contextRepository.save(context);
            
            // Update in memory system if enabled
            if (memoryIntegrationEnabled && memoryService != null) {
                memoryService.updateContextInMemory(context);
            }
        }
        
        return true;
    }

    /**
     * Unsubscribe an agent from updates for a shared context.
     *
     * @param contextId ID of the context
     * @param agentId ID of the agent unsubscribing
     * @return True if unsubscription was successful, false otherwise
     * @throws NoSuchElementException if context not found
     */
    @Transactional
    public boolean unsubscribe(String contextId, String agentId) {
        SharedContext context = contextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Context not found: " + contextId));
        
        // Remove from subscribers
        if (context.getSubscribers().contains(agentId)) {
            context.getSubscribers().remove(agentId);
            
            // Update context
            contextRepository.save(context);
            
            // Update in memory system if enabled
            if (memoryIntegrationEnabled && memoryService != null) {
                memoryService.updateContextInMemory(context);
            }
            
            return true;
        }
        
        return false;
    }

    /**
     * Get a specific version of a shared context.
     *
     * @param contextId ID of the context
     * @param versionId ID of the version to retrieve
     * @param agentId ID of the agent requesting the version
     * @return The context content at the specified version
     * @throws NoSuchElementException if context or version not found
     * @throws SecurityException if agent does not have access
     */
    @Transactional(readOnly = true)
    public Map<String, Object> getContextVersion(
            String contextId,
            String versionId,
            String agentId) {
        
        SharedContext context = contextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Context not found: " + contextId));
        
        // Check if agent can read
        if (!canAgentPerform(context, agentId, "READ")) {
            throw new SecurityException("Agent does not have read permission: " + agentId);
        }
        
        // Find the specified version
        ContextVersion targetVersion = versionRepository.findById(versionId)
                .orElseThrow(() -> new NoSuchElementException("Version not found: " + versionId));
        
        // Reconstruct content at this version
        return reconstructVersionContent(context, targetVersion);
    }

    /**
     * Compare two versions of a shared context.
     *
     * @param contextId ID of the context
     * @param versionId1 ID of the first version
     * @param versionId2 ID of the second version
     * @param agentId ID of the agent requesting the comparison
     * @return A dictionary containing differences between the versions
     * @throws NoSuchElementException if context or version not found
     * @throws SecurityException if agent does not have access
     */
    @Transactional(readOnly = true)
    public Map<String, Object> compareVersions(
            String contextId,
            String versionId1,
            String versionId2,
            String agentId) {
        
        SharedContext context = contextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Context not found: " + contextId));
        
        // Check if agent can read
        if (!canAgentPerform(context, agentId, "READ")) {
            throw new SecurityException("Agent does not have read permission: " + agentId);
        }
        
        // Get content for both versions
        Map<String, Object> content1 = getContextVersion(contextId, versionId1, agentId);
        Map<String, Object> content2 = getContextVersion(contextId, versionId2, agentId);
        
        // Find differences
        Map<String, Object> differences = findDifferences(content1, content2);
        
        // Get metadata for both versions
        ContextVersion version1 = versionRepository.findById(versionId1).orElse(null);
        ContextVersion version2 = versionRepository.findById(versionId2).orElse(null);
        
        Map<String, Object> metadata1 = version1 != null ? version1.getMetadata() : Collections.emptyMap();
        Map<String, Object> metadata2 = version2 != null ? version2.getMetadata() : Collections.emptyMap();
        
        return Map.of(
                "differences", differences,
                "version1", Map.of(
                        "id", versionId1,
                        "timestamp", version1 != null ? version1.getTimestamp() : null,
                        "agentId", version1 != null ? version1.getAgentId() : null,
                        "metadata", metadata1
                ),
                "version2", Map.of(
                        "id", versionId2,
                        "timestamp", version2 != null ? version2.getTimestamp() : null,
                        "agentId", version2 != null ? version2.getAgentId() : null,
                        "metadata", metadata2
                )
        );
    }

    /**
     * Revert a shared context to a previous version.
     *
     * @param contextId ID of the context
     * @param versionId ID of the version to revert to
     * @param agentId ID of the agent performing the revert
     * @return The reverted context
     * @throws NoSuchElementException if context or version not found
     * @throws SecurityException if agent does not have access
     */
    @Transactional
    public SharedContext revertToVersion(
            String contextId,
            String versionId,
            String agentId) {
        
        SharedContext context = contextRepository.findById(contextId)
                .orElseThrow(() -> new NoSuchElementException("Context not found: " + contextId));
        
        // Check if agent can update
        if (!canAgentPerform(context, agentId, "UPDATE")) {
            throw new SecurityException("Agent does not have update permission: " + agentId);
        }
        
        // Get content at the specified version
        Map<String, Object> versionContent = getContextVersion(contextId, versionId, agentId);
        
        // Create change
        ContextChange change = new ContextChange(
                agentId,
                LocalDateTime.now(),
                "UPDATE",
                "/",
                context.getContent(),
                versionContent,
                Collections.singletonMap("revertedTo", versionId)
        );
        
        // Update content
        context.setContent(deepCopy(versionContent));
        
        // Create new version
        ContextVersion newVersion = new ContextVersion();
        newVersion.setVersionId(UUID.randomUUID().toString());
        newVersion.setTimestamp(LocalDateTime.now());
        newVersion.setAgentId(agentId);
        newVersion.setParentVersionId(context.getCurrentVersionId());
        newVersion.setChanges(Collections.singletonList(change));
        newVersion.setMetadata(Collections.singletonMap("revertedTo", versionId));
        newVersion.computeHash();
        
        // Save version
        versionRepository.save(newVersion);
        
        // Update context
        context.setCurrentVersionId(newVersion.getVersionId());
        context.setUpdatedAt(LocalDateTime.now());
        
        // Save context
        SharedContext savedContext = contextRepository.save(context);
        
        // Notify subscribers
        notifySubscribers(context, Collections.singletonList(change));
        
        // Update in memory system if enabled
        if (memoryIntegrationEnabled && memoryService != null) {
            memoryService.updateContextInMemory(savedContext);
        }
        
        return savedContext;
    }

    /**
     * Search for shared contexts matching a query.
     *
     * @param query Search query
     * @param contextType Optional filter by context type
     * @param agentId Optional filter by agent with access
     * @return List of matching contexts
     */
    @Transactional(readOnly = true)
    public List<SharedContext> searchContexts(
            String query,
            String contextType,
            String agentId) {
        
        // If memory integration is enabled, try to search in memory first
        if (memoryIntegrationEnabled && memoryService != null) {
            List<SharedContext> memoryResults = memoryService.searchContextsInMemory(query, contextType, agentId);
            if (!memoryResults.isEmpty()) {
                return memoryResults;
            }
        }
        
        // Search in database
        List<SharedContext> results = new ArrayList<>();
        
        if (contextType != null && agentId != null) {
            results = contextRepository.findByContextTypeAndNameContainingIgnoreCase(contextType, query);
        } else if (contextType != null) {
            results = contextRepository.findByContextTypeAndNameContainingIgnoreCase(contextType, query);
        } else if (agentId != null) {
            results = contextRepository.findByNameContainingIgnoreCase(query);
        } else {
            results = contextRepository.findByNameContainingIgnoreCase(query);
        }
        
        // Filter by agent access if needed
        if (agentId != null) {
            results = results.stream()
                    .filter(context -> canAgentPerform(context, agentId, "READ"))
                    .collect(Collectors.toList());
        }
        
        return results;
    }

    /**
     * Check if an agent can perform the specified operation on a context.
     *
     * @param context The context
     * @param agentId ID of the agent
     * @param operation The operation to check
     * @return True if the agent can perform the operation, false otherwise
     */
    private boolean canAgentPerform(SharedContext context, String agentId, String operation) {
        // Owner can do anything
        if (agentId.equals(context.getOwnerId())) {
            return true;
        }
        
        // Check access control
        ContextAccess access = getAgentAccess(context, agentId);
        return access != null && canPerform(access, operation);
    }

    /**
     * Get access control for a specific agent.
     *
     * @param context The context
     * @param agentId ID of the agent
     * @return The access control, or null if not found
     */
    private ContextAccess getAgentAccess(SharedContext context, String agentId) {
        for (ContextAccess access : context.getAccessControl()) {
            if (access.getAgentId().equals(agentId) && !isExpired(access)) {
                return access;
            }
        }
        return null;
    }

    /**
     * Check if access has expired.
     *
     * @param access The access control
     * @return True if access has expired, false otherwise
     */
    private boolean isExpired(ContextAccess access) {
        return access.getExpiresAt() != null && LocalDateTime.now().isAfter(access.getExpiresAt());
    }

    /**
     * Check if the agent can perform the specified operation.
     *
     * @param access The access control
     * @param operation The operation to check
     * @return True if the agent can perform the operation, false otherwise
     */
    private boolean canPerform(ContextAccess access, String operation) {
        if (isExpired(access)) {
            return false;
        }
        
        if (access.getAccessLevel().equals("ADMIN")) {
            return true;
        }
        
        if (access.getAccessLevel().equals("READ_WRITE")) {
            return !operation.equals("DELETE");
        }
        
        if (access.getAccessLevel().equals("READ_ONLY")) {
            return operation.equals("READ") || operation.equals("SUBSCRIBE");
        }
        
        return false;
    }

    /**
     * Get a value at a specific path in the content.
     *
     * @param content The content
     * @param path The path
     * @return The value at the path, or null if not found
     */
    @SuppressWarnings("unchecked")
    private Object getValueAtPath(Map<String, Object> content, String path) {
        if (path.equals("/")) {
            return content;
        }
        
        String[] parts = path.replaceAll("^/", "").split("/");
        Map<String, Object> current = content;
        
        for (int i = 0; i < parts.length - 1; i++) {
            String part = parts[i];
            if (current.containsKey(part) && current.get(part) instanceof Map) {
                current = (Map<String, Object>) current.get(part);
            } else {
                return null;
            }
        }
        
        return current.get(parts[parts.length - 1]);
    }

    /**
     * Set a value at a specific path in the content.
     *
     * @param content The content
     * @param path The path
     * @param value The value to set
     */
    @SuppressWarnings("unchecked")
    private void setValueAtPath(Map<String, Object> content, String path, Object value) {
        if (path.equals("/")) {
            // Replace entire content
            content.clear();
            if (value instanceof Map) {
                content.putAll((Map<String, Object>) value);
            }
            return;
        }
        
        String[] parts = path.replaceAll("^/", "").split("/");
        Map<String, Object> current = content;
        
        // Navigate to the parent of the target
        for (int i = 0; i < parts.length - 1; i++) {
            String part = parts[i];
            if (!current.containsKey(part) || !(current.get(part) instanceof Map)) {
                current.put(part, new HashMap<String, Object>());
            }
            current = (Map<String, Object>) current.get(part);
        }
        
        // Set the value
        current.put(parts[parts.length - 1], value);
    }

    /**
     * Merge two content dictionaries.
     *
     * @param targetContent The target content
     * @param sourceContent The source content
     * @param conflictResolution Strategy for resolving conflicts
     * @return The merged content
     */
    private Map<String, Object> mergeContents(
            Map<String, Object> targetContent,
            Map<String, Object> sourceContent,
            String conflictResolution) {
        
        Map<String, Object> result = deepCopy(targetContent);
        
        mergeRecursive(result, sourceContent, "", conflictResolution);
        
        return result;
    }

    /**
     * Recursively merge two content dictionaries.
     *
     * @param target The target content
     * @param source The source content
     * @param path The current path
     * @param conflictResolution Strategy for resolving conflicts
     */
    @SuppressWarnings("unchecked")
    private void mergeRecursive(
            Map<String, Object> target,
            Map<String, Object> source,
            String path,
            String conflictResolution) {
        
        for (Map.Entry<String, Object> entry : source.entrySet()) {
            String key = entry.getKey();
            Object value = entry.getValue();
            String fullPath = path.isEmpty() ? key : path + "/" + key;
            
            if (target.containsKey(key)) {
                // Handle conflict
                if (value instanceof Map && target.get(key) instanceof Map) {
                    // Recursively merge dictionaries
                    mergeRecursive(
                            (Map<String, Object>) target.get(key),
                            (Map<String, Object>) value,
                            fullPath,
                            conflictResolution
                    );
                } else {
                    // Resolve conflict based on strategy
                    if (conflictResolution.equals("source")) {
                        target.put(key, deepCopy(value));
                    } else if (conflictResolution.equals("target")) {
                        // Keep target value
                    } else {  // "latest" or default
                        target.put(key, deepCopy(value));
                    }
                }
            } else {
                // No conflict, just add
                target.put(key, deepCopy(value));
            }
        }
    }

    /**
     * Notify subscribers of changes to a context.
     *
     * @param context The context
     * @param changes The changes
     */
    private void notifySubscribers(SharedContext context, List<ContextChange> changes) {
        // In a real implementation, this would send notifications to subscribers
        // For now, we'll just log the notifications
        for (String subscriberId : context.getSubscribers()) {
            logger.info("Notifying agent {} of {} changes to context {}", 
                       subscriberId, changes.size(), context.getId());
        }
    }

    /**
     * Reconstruct the content of a context at a specific version.
     *
     * @param context The context
     * @param targetVersion The target version
     * @return The reconstructed content
     */
    private Map<String, Object> reconstructVersionContent(
            SharedContext context,
            ContextVersion targetVersion) {
        
        // Find the path from the target version to the initial version
        List<ContextVersion> versionPath = new ArrayList<>();
        ContextVersion currentVersion = targetVersion;
        
        while (currentVersion != null) {
            versionPath.add(currentVersion);
            
            if (currentVersion.getParentVersionId() == null) {
                break;
            }
            
            // Find parent version
            currentVersion = versionRepository.findById(currentVersion.getParentVersionId()).orElse(null);
        }
        
        // Reverse to start from initial version
        Collections.reverse(versionPath);
        
        // Start with empty content
        Map<String, Object> content = new HashMap<>();
        
        // Apply changes in order
        for (ContextVersion version : versionPath) {
            for (ContextChange change : version.getChanges()) {
                if (change.getOperation().equals("CREATE") || change.getOperation().equals("UPDATE")) {
                    setValueAtPath(content, change.getPath(), deepCopy(change.getNewValue()));
                } else if (change.getOperation().equals("DELETE")) {
                    // Handle delete operation if needed
                }
            }
        }
        
        return content;
    }

    /**
     * Find differences between two content dictionaries.
     *
     * @param content1 The first content
     * @param content2 The second content
     * @return The differences
     */
    private Map<String, Object> findDifferences(
            Map<String, Object> content1,
            Map<String, Object> content2) {
        
        Map<String, Object> differences = new HashMap<>();
        differences.put("added", new HashMap<String, Object>());
        differences.put("removed", new HashMap<String, Object>());
        differences.put("modified", new HashMap<String, Object>());
        
        compareRecursive(content1, content2, "", 
                        (Map<String, Object>) differences.get("added"),
                        (Map<String, Object>) differences.get("removed"),
                        (Map<String, Object>) differences.get("modified"));
        
        return differences;
    }

    /**
     * Recursively compare two content dictionaries.
     *
     * @param dict1 The first dictionary
     * @param dict2 The second dictionary
     * @param path The current path
     * @param added Map to store added items
     * @param removed Map to store removed items
     * @param modified Map to store modified items
     */
    @SuppressWarnings("unchecked")
    private void compareRecursive(
            Map<String, Object> dict1,
            Map<String, Object> dict2,
            String path,
            Map<String, Object> added,
            Map<String, Object> removed,
            Map<String, Object> modified) {
        
        // Find keys in dict2 that are not in dict1 (added)
        for (String key : dict2.keySet()) {
            if (!dict1.containsKey(key)) {
                String fullPath = path.isEmpty() ? key : path + "/" + key;
                added.put(fullPath, dict2.get(key));
            }
        }
        
        // Find keys in dict1 that are not in dict2 (removed)
        for (String key : dict1.keySet()) {
            if (!dict2.containsKey(key)) {
                String fullPath = path.isEmpty() ? key : path + "/" + key;
                removed.put(fullPath, dict1.get(key));
            }
        }
        
        // Find keys that are in both but with different values (modified)
        for (String key : dict1.keySet()) {
            if (dict2.containsKey(key)) {
                String fullPath = path.isEmpty() ? key : path + "/" + key;
                
                Object value1 = dict1.get(key);
                Object value2 = dict2.get(key);
                
                if (value1 instanceof Map && value2 instanceof Map) {
                    // Recursively compare dictionaries
                    compareRecursive(
                            (Map<String, Object>) value1,
                            (Map<String, Object>) value2,
                            fullPath,
                            added,
                            removed,
                            modified
                    );
                } else if (!Objects.equals(value1, value2)) {
                    Map<String, Object> diff = new HashMap<>();
                    diff.put("from", value1);
                    diff.put("to", value2);
                    modified.put(fullPath, diff);
                }
            }
        }
    }

    /**
     * Create a deep copy of an object.
     *
     * @param obj The object to copy
     * @return The deep copy
     */
    @SuppressWarnings("unchecked")
    private <T> T deepCopy(T obj) {
        if (obj == null) {
            return null;
        }
        
        if (obj instanceof Map) {
            Map<String, Object> result = new HashMap<>();
            for (Map.Entry<String, Object> entry : ((Map<String, Object>) obj).entrySet()) {
                result.put(entry.getKey(), deepCopy(entry.getValue()));
            }
            return (T) result;
        } else if (obj instanceof List) {
            List<Object> result = new ArrayList<>();
            for (Object item : (List<Object>) obj) {
                result.add(deepCopy(item));
            }
            return (T) result;
        } else if (obj instanceof Set) {
            Set<Object> result = new HashSet<>();
            for (Object item : (Set<Object>) obj) {
                result.add(deepCopy(item));
            }
            return (T) result;
        } else {
            // Primitive types, strings, etc. are immutable
            return obj;
        }
    }
}
