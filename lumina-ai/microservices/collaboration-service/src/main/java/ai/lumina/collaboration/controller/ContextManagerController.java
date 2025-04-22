package ai.lumina.collaboration.controller;

import ai.lumina.collaboration.model.ContextItem;
import ai.lumina.collaboration.service.ContextManagerService;
import com.fasterxml.jackson.core.JsonProcessingException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;

/**
 * REST controller for managing context items in the collaboration system.
 */
@RestController
@RequestMapping("/api/v1/collaboration/context")
@RequiredArgsConstructor
@Slf4j
public class ContextManagerController {

    private final ContextManagerService contextManagerService;

    /**
     * Share context.
     *
     * @param request the context sharing request
     * @return the created context item
     */
    @PostMapping
    public ResponseEntity<ContextItem> shareContext(@RequestBody ContextSharingRequest request) {
        log.info("Received request to share context: {} for {}/{}", 
                request.getKey(), request.getScope(), request.getScopeId());
        
        try {
            ContextItem contextItem = contextManagerService.shareContext(
                    request.getKey(),
                    request.getValue(),
                    request.getContextType(),
                    request.getScope(),
                    request.getScopeId(),
                    request.getAgentId(),
                    request.getExpiresAt()
            );
            
            return ResponseEntity.status(HttpStatus.CREATED).body(contextItem);
        } catch (JsonProcessingException e) {
            log.error("Failed to serialize context value: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }

    /**
     * Get a context item by ID.
     *
     * @param contextId the context ID
     * @return the context item, or 404 if not found
     */
    @GetMapping("/{contextId}")
    public ResponseEntity<ContextItem> getContext(@PathVariable String contextId) {
        log.info("Received request to get context: {}", contextId);
        
        return contextManagerService.getContext(contextId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get context items by key.
     *
     * @param key the context key
     * @return list of context items
     */
    @GetMapping("/by-key")
    public ResponseEntity<List<ContextItem>> getContextByKey(@RequestParam String key) {
        log.info("Received request to get context by key: {}", key);
        
        List<ContextItem> contextItems = contextManagerService.getContextByKey(key);
        return ResponseEntity.ok(contextItems);
    }

    /**
     * Get context items by scope and scope ID.
     *
     * @param scope the context scope
     * @param scopeId the scope ID
     * @return list of context items
     */
    @GetMapping("/by-scope")
    public ResponseEntity<List<ContextItem>> getContextByScope(
            @RequestParam ContextItem.ContextScope scope,
            @RequestParam String scopeId) {
        
        log.info("Received request to get context by scope: {}/{}", scope, scopeId);
        
        List<ContextItem> contextItems = contextManagerService.getContextByScope(scope, scopeId);
        return ResponseEntity.ok(contextItems);
    }

    /**
     * Get context items by scope, scope ID, and context type.
     *
     * @param scope the context scope
     * @param scopeId the scope ID
     * @param contextType the context type
     * @return list of context items
     */
    @GetMapping("/by-type-and-scope")
    public ResponseEntity<List<ContextItem>> getContextByTypeAndScope(
            @RequestParam ContextItem.ContextScope scope,
            @RequestParam String scopeId,
            @RequestParam ContextItem.ContextType contextType) {
        
        log.info("Received request to get context by type and scope: {}/{}/{}", contextType, scope, scopeId);
        
        List<ContextItem> contextItems = contextManagerService.getContextByTypeAndScope(scope, scopeId, contextType);
        return ResponseEntity.ok(contextItems);
    }

    /**
     * Get context items accessible to an agent.
     *
     * @param agentId the agent ID
     * @return list of context items
     */
    @GetMapping("/accessible-to/{agentId}")
    public ResponseEntity<List<ContextItem>> getContextAccessibleToAgent(@PathVariable String agentId) {
        log.info("Received request to get context accessible to agent: {}", agentId);
        
        List<ContextItem> contextItems = contextManagerService.getContextAccessibleToAgent(agentId);
        return ResponseEntity.ok(contextItems);
    }

    /**
     * Update a context item's value.
     *
     * @param contextId the context ID
     * @param request the value update request
     * @return the updated context item, or 404 if not found
     */
    @PutMapping("/{contextId}/value")
    public ResponseEntity<ContextItem> updateContextValue(
            @PathVariable String contextId,
            @RequestBody ValueUpdateRequest request) {
        
        log.info("Received request to update value for context: {}", contextId);
        
        try {
            return contextManagerService.updateContextValue(contextId, request.getValue())
                    .map(ResponseEntity::ok)
                    .orElse(ResponseEntity.notFound().build());
        } catch (JsonProcessingException e) {
            log.error("Failed to serialize context value: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }

    /**
     * Delete a context item.
     *
     * @param contextId the context ID
     * @return 204 if successful, 404 if context not found
     */
    @DeleteMapping("/{contextId}")
    public ResponseEntity<Void> deleteContext(@PathVariable String contextId) {
        log.info("Received request to delete context: {}", contextId);
        
        boolean success = contextManagerService.deleteContext(contextId);
        return success ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }

    /**
     * Clean up expired context items.
     *
     * @return number of items deleted
     */
    @PostMapping("/cleanup")
    public ResponseEntity<CleanupResponse> cleanupExpiredContext() {
        log.info("Received request to clean up expired context items");
        
        int count = contextManagerService.cleanupExpiredContext();
        CleanupResponse response = new CleanupResponse(count);
        return ResponseEntity.ok(response);
    }

    /**
     * Context sharing request.
     */
    public static class ContextSharingRequest {
        private String key;
        private Object value;
        private ContextItem.ContextType contextType;
        private ContextItem.ContextScope scope;
        private String scopeId;
        private String agentId;
        private LocalDateTime expiresAt;

        // Getters and setters
        public String getKey() { return key; }
        public void setKey(String key) { this.key = key; }
        
        public Object getValue() { return value; }
        public void setValue(Object value) { this.value = value; }
        
        public ContextItem.ContextType getContextType() { return contextType; }
        public void setContextType(ContextItem.ContextType contextType) { this.contextType = contextType; }
        
        public ContextItem.ContextScope getScope() { return scope; }
        public void setScope(ContextItem.ContextScope scope) { this.scope = scope; }
        
        public String getScopeId() { return scopeId; }
        public void setScopeId(String scopeId) { this.scopeId = scopeId; }
        
        public String getAgentId() { return agentId; }
        public void setAgentId(String agentId) { this.agentId = agentId; }
        
        public LocalDateTime getExpiresAt() { return expiresAt; }
        public void setExpiresAt(LocalDateTime expiresAt) { this.expiresAt = expiresAt; }
    }

    /**
     * Value update request.
     */
    public static class ValueUpdateRequest {
        private Object value;

        // Getters and setters
        public Object getValue() { return value; }
        public void setValue(Object value) { this.value = value; }
    }

    /**
     * Cleanup response.
     */
    public static class CleanupResponse {
        private int deletedCount;

        public CleanupResponse(int deletedCount) {
            this.deletedCount = deletedCount;
        }

        // Getters and setters
        public int getDeletedCount() { return deletedCount; }
        public void setDeletedCount(int deletedCount) { this.deletedCount = deletedCount; }
    }
}
