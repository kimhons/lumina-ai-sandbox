package ai.lumina.collaboration.controller;

import ai.lumina.collaboration.model.MemoryItem;
import ai.lumina.collaboration.service.SharedMemoryService;
import com.fasterxml.jackson.core.JsonProcessingException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;

/**
 * REST controller for managing shared memory items in the collaboration system.
 */
@RestController
@RequestMapping("/api/v1/collaboration/memory")
@RequiredArgsConstructor
@Slf4j
public class SharedMemoryController {

    private final SharedMemoryService sharedMemoryService;

    /**
     * Create a new memory item.
     *
     * @param request the memory creation request
     * @return the created memory item
     */
    @PostMapping
    public ResponseEntity<MemoryItem> createMemory(@RequestBody MemoryCreationRequest request) {
        log.info("Received request to create memory: {} for {}/{}", 
                request.getKey(), request.getScope(), request.getScopeId());
        
        try {
            MemoryItem memoryItem = sharedMemoryService.createMemory(
                    request.getKey(),
                    request.getValue(),
                    request.getMemoryType(),
                    request.getScope(),
                    request.getScopeId(),
                    request.getAgentId(),
                    request.getImportance(),
                    request.getTags()
            );
            
            return ResponseEntity.status(HttpStatus.CREATED).body(memoryItem);
        } catch (JsonProcessingException e) {
            log.error("Failed to serialize memory value: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }

    /**
     * Get a memory item by ID.
     *
     * @param memoryId the memory ID
     * @return the memory item, or 404 if not found
     */
    @GetMapping("/{memoryId}")
    public ResponseEntity<MemoryItem> getMemory(@PathVariable String memoryId) {
        log.info("Received request to get memory: {}", memoryId);
        
        return sharedMemoryService.getMemory(memoryId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get memory items by key.
     *
     * @param key the memory key
     * @return list of memory items
     */
    @GetMapping("/by-key")
    public ResponseEntity<List<MemoryItem>> getMemoriesByKey(@RequestParam String key) {
        log.info("Received request to get memories by key: {}", key);
        
        List<MemoryItem> memoryItems = sharedMemoryService.getMemoriesByKey(key);
        return ResponseEntity.ok(memoryItems);
    }

    /**
     * Get memory items by scope and scope ID.
     *
     * @param scope the memory scope
     * @param scopeId the scope ID
     * @return list of memory items
     */
    @GetMapping("/by-scope")
    public ResponseEntity<List<MemoryItem>> getMemoriesByScope(
            @RequestParam MemoryItem.MemoryScope scope,
            @RequestParam String scopeId) {
        
        log.info("Received request to get memories by scope: {}/{}", scope, scopeId);
        
        List<MemoryItem> memoryItems = sharedMemoryService.getMemoriesByScope(scope, scopeId);
        return ResponseEntity.ok(memoryItems);
    }

    /**
     * Get memory items by memory type.
     *
     * @param memoryType the memory type
     * @return list of memory items
     */
    @GetMapping("/by-type")
    public ResponseEntity<List<MemoryItem>> getMemoriesByType(
            @RequestParam MemoryItem.MemoryType memoryType) {
        
        log.info("Received request to get memories by type: {}", memoryType);
        
        List<MemoryItem> memoryItems = sharedMemoryService.getMemoriesByType(memoryType);
        return ResponseEntity.ok(memoryItems);
    }

    /**
     * Get memory items by tag.
     *
     * @param tag the tag
     * @return list of memory items
     */
    @GetMapping("/by-tag")
    public ResponseEntity<List<MemoryItem>> getMemoriesByTag(@RequestParam String tag) {
        log.info("Received request to get memories by tag: {}", tag);
        
        List<MemoryItem> memoryItems = sharedMemoryService.getMemoriesByTag(tag);
        return ResponseEntity.ok(memoryItems);
    }

    /**
     * Get memory items by multiple tags (must have all tags).
     *
     * @param tags the set of tags
     * @return list of memory items
     */
    @GetMapping("/by-all-tags")
    public ResponseEntity<List<MemoryItem>> getMemoriesByAllTags(@RequestParam Set<String> tags) {
        log.info("Received request to get memories by all tags: {}", tags);
        
        List<MemoryItem> memoryItems = sharedMemoryService.getMemoriesByAllTags(tags);
        return ResponseEntity.ok(memoryItems);
    }

    /**
     * Get memory items by multiple tags (must have at least one tag).
     *
     * @param tags the set of tags
     * @return list of memory items
     */
    @GetMapping("/by-any-tag")
    public ResponseEntity<List<MemoryItem>> getMemoriesByAnyTag(@RequestParam Set<String> tags) {
        log.info("Received request to get memories by any tag: {}", tags);
        
        List<MemoryItem> memoryItems = sharedMemoryService.getMemoriesByAnyTag(tags);
        return ResponseEntity.ok(memoryItems);
    }

    /**
     * Get memory items accessible to an agent.
     *
     * @param agentId the agent ID
     * @return list of memory items
     */
    @GetMapping("/accessible-to/{agentId}")
    public ResponseEntity<List<MemoryItem>> getMemoriesAccessibleToAgent(@PathVariable String agentId) {
        log.info("Received request to get memories accessible to agent: {}", agentId);
        
        List<MemoryItem> memoryItems = sharedMemoryService.getMemoriesAccessibleToAgent(agentId);
        return ResponseEntity.ok(memoryItems);
    }

    /**
     * Update a memory item's value.
     *
     * @param memoryId the memory ID
     * @param request the value update request
     * @return the updated memory item, or 404 if not found
     */
    @PutMapping("/{memoryId}/value")
    public ResponseEntity<MemoryItem> updateMemoryValue(
            @PathVariable String memoryId,
            @RequestBody ValueUpdateRequest request) {
        
        log.info("Received request to update value for memory: {}", memoryId);
        
        try {
            return sharedMemoryService.updateMemoryValue(memoryId, request.getValue())
                    .map(ResponseEntity::ok)
                    .orElse(ResponseEntity.notFound().build());
        } catch (JsonProcessingException e) {
            log.error("Failed to serialize memory value: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }

    /**
     * Update a memory item's importance.
     *
     * @param memoryId the memory ID
     * @param request the importance update request
     * @return the updated memory item, or 404 if not found
     */
    @PutMapping("/{memoryId}/importance")
    public ResponseEntity<MemoryItem> updateMemoryImportance(
            @PathVariable String memoryId,
            @RequestBody ImportanceUpdateRequest request) {
        
        log.info("Received request to update importance for memory: {} to {}", 
                memoryId, request.getImportance());
        
        return sharedMemoryService.updateMemoryImportance(memoryId, request.getImportance())
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Update a memory item's tags.
     *
     * @param memoryId the memory ID
     * @param request the tags update request
     * @return the updated memory item, or 404 if not found
     */
    @PutMapping("/{memoryId}/tags")
    public ResponseEntity<MemoryItem> updateMemoryTags(
            @PathVariable String memoryId,
            @RequestBody TagsUpdateRequest request) {
        
        log.info("Received request to update tags for memory: {}", memoryId);
        
        return sharedMemoryService.updateMemoryTags(memoryId, request.getTags())
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Delete a memory item.
     *
     * @param memoryId the memory ID
     * @return 204 if successful, 404 if memory not found
     */
    @DeleteMapping("/{memoryId}")
    public ResponseEntity<Void> deleteMemory(@PathVariable String memoryId) {
        log.info("Received request to delete memory: {}", memoryId);
        
        boolean success = sharedMemoryService.deleteMemory(memoryId);
        return success ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }

    /**
     * Find important memories.
     *
     * @param minImportance the minimum importance
     * @return list of memory items
     */
    @GetMapping("/important")
    public ResponseEntity<List<MemoryItem>> findImportantMemories(
            @RequestParam Float minImportance) {
        
        log.info("Received request to find important memories with min importance: {}", minImportance);
        
        List<MemoryItem> memoryItems = sharedMemoryService.findImportantMemories(minImportance);
        return ResponseEntity.ok(memoryItems);
    }

    /**
     * Find frequently accessed memories.
     *
     * @param minAccessCount the minimum access count
     * @return list of memory items
     */
    @GetMapping("/frequently-accessed")
    public ResponseEntity<List<MemoryItem>> findFrequentlyAccessedMemories(
            @RequestParam Integer minAccessCount) {
        
        log.info("Received request to find frequently accessed memories with min count: {}", minAccessCount);
        
        List<MemoryItem> memoryItems = sharedMemoryService.findFrequentlyAccessedMemories(minAccessCount);
        return ResponseEntity.ok(memoryItems);
    }

    /**
     * Find recently accessed memories.
     *
     * @param since the time threshold
     * @return list of memory items
     */
    @GetMapping("/recently-accessed")
    public ResponseEntity<List<MemoryItem>> findRecentlyAccessedMemories(
            @RequestParam LocalDateTime since) {
        
        log.info("Received request to find recently accessed memories since: {}", since);
        
        List<MemoryItem> memoryItems = sharedMemoryService.findRecentlyAccessedMemories(since);
        return ResponseEntity.ok(memoryItems);
    }

    /**
     * Memory creation request.
     */
    public static class MemoryCreationRequest {
        private String key;
        private Object value;
        private MemoryItem.MemoryType memoryType;
        private MemoryItem.MemoryScope scope;
        private String scopeId;
        private String agentId;
        private Float importance;
        private Set<String> tags;

        // Getters and setters
        public String getKey() { return key; }
        public void setKey(String key) { this.key = key; }
        
        public Object getValue() { return value; }
        public void setValue(Object value) { this.value = value; }
        
        public MemoryItem.MemoryType getMemoryType() { return memoryType; }
        public void setMemoryType(MemoryItem.MemoryType memoryType) { this.memoryType = memoryType; }
        
        public MemoryItem.MemoryScope getScope() { return scope; }
        public void setScope(MemoryItem.MemoryScope scope) { this.scope = scope; }
        
        public String getScopeId() { return scopeId; }
        public void setScopeId(String scopeId) { this.scopeId = scopeId; }
        
        public String getAgentId() { return agentId; }
        public void setAgentId(String agentId) { this.agentId = agentId; }
        
        public Float getImportance() { return importance; }
        public void setImportance(Float importance) { this.importance = importance; }
        
        public Set<String> getTags() { return tags; }
        public void setTags(Set<String> tags) { this.tags = tags; }
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
     * Importance update request.
     */
    public static class ImportanceUpdateRequest {
        private Float importance;

        // Getters and setters
        public Float getImportance() { return importance; }
        public void setImportance(Float importance) { this.importance = importance; }
    }

    /**
     * Tags update request.
     */
    public static class TagsUpdateRequest {
        private Set<String> tags;

        // Getters and setters
        public Set<String> getTags() { return tags; }
        public void setTags(Set<String> tags) { this.tags = tags; }
    }
}
