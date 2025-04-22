package ai.lumina.collaboration.controller;

import ai.lumina.collaboration.model.SharedContext;
import ai.lumina.collaboration.service.SharedContextService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;

/**
 * REST controller for shared context management operations.
 */
@RestController
@RequestMapping("/api/v1/collaboration/contexts")
public class SharedContextController {

    private static final Logger logger = LoggerFactory.getLogger(SharedContextController.class);

    @Autowired
    private SharedContextService contextService;

    /**
     * Create a new shared context.
     *
     * @param request The context creation request
     * @return The created context
     */
    @PostMapping
    public ResponseEntity<SharedContext> createContext(@RequestBody Map<String, Object> request) {
        logger.info("Received request to create shared context: {}", request.get("name"));
        
        String name = (String) request.get("name");
        String contextType = (String) request.get("contextType");
        String ownerId = (String) request.get("ownerId");
        @SuppressWarnings("unchecked")
        Map<String, Object> initialContent = (Map<String, Object>) request.get("initialContent");
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> accessControl = (List<Map<String, Object>>) request.get("accessControl");
        
        SharedContext context = contextService.createContext(name, contextType, ownerId, initialContent, accessControl);
        return ResponseEntity.ok(context);
    }

    /**
     * Get a shared context by ID.
     *
     * @param contextId The ID of the context
     * @param agentId The ID of the agent requesting the context
     * @return The context
     */
    @GetMapping("/{contextId}")
    public ResponseEntity<SharedContext> getContext(
            @PathVariable String contextId,
            @RequestParam String agentId) {
        
        logger.info("Received request to get context ID: {} by agent: {}", contextId, agentId);
        
        try {
            SharedContext context = contextService.getContext(contextId, agentId);
            return ResponseEntity.ok(context);
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (SecurityException e) {
            return ResponseEntity.status(403).build();
        }
    }

    /**
     * Update a shared context.
     *
     * @param contextId The ID of the context to update
     * @param request The update request
     * @return The updated context
     */
    @PutMapping("/{contextId}")
    public ResponseEntity<SharedContext> updateContext(
            @PathVariable String contextId,
            @RequestBody Map<String, Object> request) {
        
        logger.info("Received request to update context ID: {}", contextId);
        
        String agentId = (String) request.get("agentId");
        @SuppressWarnings("unchecked")
        Map<String, Object> updates = (Map<String, Object>) request.get("updates");
        @SuppressWarnings("unchecked")
        Map<String, Object> metadata = (Map<String, Object>) request.get("metadata");
        
        try {
            SharedContext context = contextService.updateContext(contextId, agentId, updates, metadata);
            return ResponseEntity.ok(context);
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (SecurityException e) {
            return ResponseEntity.status(403).build();
        }
    }

    /**
     * Merge two shared contexts.
     *
     * @param targetContextId The ID of the target context
     * @param request The merge request
     * @return The merged context
     */
    @PostMapping("/{targetContextId}/merge")
    public ResponseEntity<SharedContext> mergeContexts(
            @PathVariable String targetContextId,
            @RequestBody Map<String, Object> request) {
        
        logger.info("Received request to merge contexts into target ID: {}", targetContextId);
        
        String sourceContextId = (String) request.get("sourceContextId");
        String agentId = (String) request.get("agentId");
        String conflictResolution = (String) request.get("conflictResolution");
        
        try {
            SharedContext context = contextService.mergeContexts(
                    targetContextId, sourceContextId, agentId, conflictResolution);
            return ResponseEntity.ok(context);
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (SecurityException e) {
            return ResponseEntity.status(403).build();
        }
    }

    /**
     * Fork a shared context.
     *
     * @param contextId The ID of the context to fork
     * @param request The fork request
     * @return The forked context
     */
    @PostMapping("/{contextId}/fork")
    public ResponseEntity<SharedContext> forkContext(
            @PathVariable String contextId,
            @RequestBody Map<String, Object> request) {
        
        logger.info("Received request to fork context ID: {}", contextId);
        
        String agentId = (String) request.get("agentId");
        String newName = (String) request.get("newName");
        
        try {
            SharedContext context = contextService.forkContext(contextId, agentId, newName);
            return ResponseEntity.ok(context);
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (SecurityException e) {
            return ResponseEntity.status(403).build();
        }
    }

    /**
     * Grant access to a shared context.
     *
     * @param contextId The ID of the context
     * @param request The access grant request
     * @return Success status
     */
    @PostMapping("/{contextId}/access")
    public ResponseEntity<Map<String, Object>> grantAccess(
            @PathVariable String contextId,
            @RequestBody Map<String, Object> request) {
        
        logger.info("Received request to grant access to context ID: {}", contextId);
        
        String grantingAgentId = (String) request.get("grantingAgentId");
        String targetAgentId = (String) request.get("targetAgentId");
        String accessLevel = (String) request.get("accessLevel");
        Double expiresIn = request.get("expiresIn") != null ? 
                ((Number) request.get("expiresIn")).doubleValue() : null;
        
        try {
            boolean success = contextService.grantAccess(
                    contextId, grantingAgentId, targetAgentId, accessLevel, expiresIn);
            return ResponseEntity.ok(Map.of("success", success));
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (SecurityException e) {
            return ResponseEntity.status(403).build();
        }
    }

    /**
     * Revoke access to a shared context.
     *
     * @param contextId The ID of the context
     * @param request The access revocation request
     * @return Success status
     */
    @DeleteMapping("/{contextId}/access")
    public ResponseEntity<Map<String, Object>> revokeAccess(
            @PathVariable String contextId,
            @RequestBody Map<String, Object> request) {
        
        logger.info("Received request to revoke access to context ID: {}", contextId);
        
        String revokingAgentId = (String) request.get("revokingAgentId");
        String targetAgentId = (String) request.get("targetAgentId");
        
        try {
            boolean success = contextService.revokeAccess(contextId, revokingAgentId, targetAgentId);
            return ResponseEntity.ok(Map.of("success", success));
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (SecurityException e) {
            return ResponseEntity.status(403).build();
        }
    }

    /**
     * Subscribe to a shared context.
     *
     * @param contextId The ID of the context
     * @param agentId The ID of the agent subscribing
     * @return Success status
     */
    @PostMapping("/{contextId}/subscribe")
    public ResponseEntity<Map<String, Object>> subscribe(
            @PathVariable String contextId,
            @RequestParam String agentId) {
        
        logger.info("Received request for agent {} to subscribe to context ID: {}", agentId, contextId);
        
        try {
            boolean success = contextService.subscribe(contextId, agentId);
            return ResponseEntity.ok(Map.of("success", success));
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (SecurityException e) {
            return ResponseEntity.status(403).build();
        }
    }

    /**
     * Unsubscribe from a shared context.
     *
     * @param contextId The ID of the context
     * @param agentId The ID of the agent unsubscribing
     * @return Success status
     */
    @DeleteMapping("/{contextId}/subscribe")
    public ResponseEntity<Map<String, Object>> unsubscribe(
            @PathVariable String contextId,
            @RequestParam String agentId) {
        
        logger.info("Received request for agent {} to unsubscribe from context ID: {}", agentId, contextId);
        
        try {
            boolean success = contextService.unsubscribe(contextId, agentId);
            return ResponseEntity.ok(Map.of("success", success));
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Get a specific version of a shared context.
     *
     * @param contextId The ID of the context
     * @param versionId The ID of the version
     * @param agentId The ID of the agent requesting the version
     * @return The context content at the specified version
     */
    @GetMapping("/{contextId}/versions/{versionId}")
    public ResponseEntity<Map<String, Object>> getContextVersion(
            @PathVariable String contextId,
            @PathVariable String versionId,
            @RequestParam String agentId) {
        
        logger.info("Received request to get version {} of context ID: {}", versionId, contextId);
        
        try {
            Map<String, Object> versionContent = contextService.getContextVersion(contextId, versionId, agentId);
            return ResponseEntity.ok(versionContent);
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (SecurityException e) {
            return ResponseEntity.status(403).build();
        }
    }

    /**
     * Compare two versions of a shared context.
     *
     * @param contextId The ID of the context
     * @param versionId1 The ID of the first version
     * @param versionId2 The ID of the second version
     * @param agentId The ID of the agent requesting the comparison
     * @return The differences between the versions
     */
    @GetMapping("/{contextId}/versions/compare")
    public ResponseEntity<Map<String, Object>> compareVersions(
            @PathVariable String contextId,
            @RequestParam String versionId1,
            @RequestParam String versionId2,
            @RequestParam String agentId) {
        
        logger.info("Received request to compare versions {} and {} of context ID: {}", 
                   versionId1, versionId2, contextId);
        
        try {
            Map<String, Object> comparison = contextService.compareVersions(
                    contextId, versionId1, versionId2, agentId);
            return ResponseEntity.ok(comparison);
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (SecurityException e) {
            return ResponseEntity.status(403).build();
        }
    }

    /**
     * Revert a shared context to a previous version.
     *
     * @param contextId The ID of the context
     * @param versionId The ID of the version to revert to
     * @param agentId The ID of the agent performing the revert
     * @return The reverted context
     */
    @PostMapping("/{contextId}/versions/{versionId}/revert")
    public ResponseEntity<SharedContext> revertToVersion(
            @PathVariable String contextId,
            @PathVariable String versionId,
            @RequestParam String agentId) {
        
        logger.info("Received request to revert context ID: {} to version: {}", contextId, versionId);
        
        try {
            SharedContext context = contextService.revertToVersion(contextId, versionId, agentId);
            return ResponseEntity.ok(context);
        } catch (NoSuchElementException e) {
            return ResponseEntity.notFound().build();
        } catch (SecurityException e) {
            return ResponseEntity.status(403).build();
        }
    }

    /**
     * Search for shared contexts.
     *
     * @param query The search query
     * @param contextType Optional filter by context type
     * @param agentId Optional filter by agent with access
     * @return List of matching contexts
     */
    @GetMapping("/search")
    public ResponseEntity<List<SharedContext>> searchContexts(
            @RequestParam String query,
            @RequestParam(required = false) String contextType,
            @RequestParam(required = false) String agentId) {
        
        logger.info("Received request to search contexts with query: {}", query);
        
        List<SharedContext> results = contextService.searchContexts(query, contextType, agentId);
        return ResponseEntity.ok(results);
    }
}
