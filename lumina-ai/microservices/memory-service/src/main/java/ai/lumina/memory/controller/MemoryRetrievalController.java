package ai.lumina.memory.controller;

import ai.lumina.memory.model.MemoryItem;
import ai.lumina.memory.service.MemoryRetrievalService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST controller for memory retrieval operations.
 */
@RestController
@RequestMapping("/api/memory/retrieval")
@RequiredArgsConstructor
@Slf4j
public class MemoryRetrievalController {

    private final MemoryRetrievalService memoryRetrievalService;

    /**
     * Retrieve memories by context.
     *
     * @param userId User ID
     * @param context Conversation context
     * @param limit Maximum number of memories to retrieve
     * @return List of relevant memory items
     */
    @GetMapping("/by-context")
    public ResponseEntity<List<MemoryItem>> retrieveByContext(
            @RequestParam String userId,
            @RequestParam String context,
            @RequestParam(defaultValue = "5") int limit) {
        
        log.info("REST request to retrieve memories by context for user {}", userId);
        List<MemoryItem> memories = memoryRetrievalService.retrieveByContext(userId, context, limit);
        return ResponseEntity.ok(memories);
    }

    /**
     * Retrieve memories by query.
     *
     * @param userId User ID
     * @param query Search query
     * @param limit Maximum number of memories to retrieve
     * @return List of relevant memory items
     */
    @GetMapping("/by-query")
    public ResponseEntity<List<MemoryItem>> retrieveByQuery(
            @RequestParam String userId,
            @RequestParam String query,
            @RequestParam(defaultValue = "5") int limit) {
        
        log.info("REST request to retrieve memories by query for user {}", userId);
        List<MemoryItem> memories = memoryRetrievalService.retrieveByQuery(userId, query, limit);
        return ResponseEntity.ok(memories);
    }

    /**
     * Retrieve memories by type.
     *
     * @param userId User ID
     * @param memoryType Memory type
     * @param limit Maximum number of memories to retrieve
     * @return List of memory items of the specified type
     */
    @GetMapping("/by-type")
    public ResponseEntity<List<MemoryItem>> retrieveByType(
            @RequestParam String userId,
            @RequestParam String memoryType,
            @RequestParam(defaultValue = "10") int limit) {
        
        log.info("REST request to retrieve memories by type for user {}", userId);
        List<MemoryItem> memories = memoryRetrievalService.retrieveByType(userId, memoryType, limit);
        return ResponseEntity.ok(memories);
    }

    /**
     * Optimize retrieval strategy based on inputs.
     *
     * @param userId User ID
     * @param context Conversation context (optional)
     * @param query Search query (optional)
     * @param memoryType Memory type (optional)
     * @param limit Maximum number of memories to retrieve
     * @return List of relevant memory items
     */
    @GetMapping("/optimize")
    public ResponseEntity<List<MemoryItem>> optimizeRetrieval(
            @RequestParam String userId,
            @RequestParam(required = false) String context,
            @RequestParam(required = false) String query,
            @RequestParam(required = false) String memoryType,
            @RequestParam(defaultValue = "10") int limit) {
        
        log.info("REST request to optimize memory retrieval for user {}", userId);
        List<MemoryItem> memories = memoryRetrievalService.optimizeRetrievalStrategy(
                userId, context, query, memoryType, limit);
        return ResponseEntity.ok(memories);
    }

    /**
     * Get diverse memories for a user.
     *
     * @param userId User ID
     * @param limit Maximum number of memories to retrieve
     * @return List of diverse memory items
     */
    @GetMapping("/diverse")
    public ResponseEntity<List<MemoryItem>> getDiverseMemories(
            @RequestParam String userId,
            @RequestParam(defaultValue = "5") int limit) {
        
        log.info("REST request to get diverse memories for user {}", userId);
        List<MemoryItem> memories = memoryRetrievalService.getDiverseMemories(userId, limit);
        return ResponseEntity.ok(memories);
    }

    /**
     * Update memory access statistics.
     *
     * @param memoryId Memory ID
     * @return Success message
     */
    @PostMapping("/access/{memoryId}")
    public ResponseEntity<Map<String, String>> updateMemoryAccess(
            @PathVariable String memoryId) {
        
        log.info("REST request to update memory access for memory {}", memoryId);
        memoryRetrievalService.updateMemoryAccess(memoryId);
        return ResponseEntity.ok(Map.of("message", "Memory access updated"));
    }
}
