package ai.lumina.memory.controller;

import ai.lumina.memory.model.PersistentMemory;
import ai.lumina.memory.model.MemoryItem;
import ai.lumina.memory.service.PersistentMemoryService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * REST controller for persistent memory operations.
 */
@RestController
@RequestMapping("/api/memory/persistent")
@RequiredArgsConstructor
@Slf4j
public class PersistentMemoryController {

    private final PersistentMemoryService persistentMemoryService;

    /**
     * Get persistent memory for a user.
     *
     * @param userId User ID
     * @return The persistent memory if found
     */
    @GetMapping("/{userId}")
    public ResponseEntity<PersistentMemory> getPersistentMemory(
            @PathVariable String userId) {
        
        log.info("REST request to get persistent memory for user {}", userId);
        Optional<PersistentMemory> persistentMemory = persistentMemoryService.getPersistentMemory(userId);
        
        return persistentMemory
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Create or update persistent memory for a user.
     *
     * @param userId User ID
     * @param summary Memory summary
     * @return The created or updated persistent memory
     */
    @PostMapping("/{userId}")
    public ResponseEntity<PersistentMemory> createOrUpdatePersistentMemory(
            @PathVariable String userId,
            @RequestBody String summary) {
        
        log.info("REST request to create or update persistent memory for user {}", userId);
        PersistentMemory persistentMemory = persistentMemoryService.createOrUpdatePersistentMemory(userId, summary);
        return ResponseEntity.ok(persistentMemory);
    }

    /**
     * Add a memory item to persistent memory.
     *
     * @param userId User ID
     * @param memoryId Memory item ID
     * @return Success message
     */
    @PostMapping("/{userId}/add/{memoryId}")
    public ResponseEntity<Map<String, String>> addMemoryToPersistentMemory(
            @PathVariable String userId,
            @PathVariable String memoryId) {
        
        log.info("REST request to add memory {} to persistent memory for user {}", memoryId, userId);
        boolean added = persistentMemoryService.addMemoryToPersistentMemory(userId, memoryId);
        
        if (added) {
            return ResponseEntity.ok(Map.of("message", "Memory added to persistent memory"));
        } else {
            return ResponseEntity.badRequest().body(Map.of("message", "Failed to add memory to persistent memory"));
        }
    }

    /**
     * Remove a memory item from persistent memory.
     *
     * @param userId User ID
     * @param memoryId Memory item ID
     * @return Success message
     */
    @DeleteMapping("/{userId}/remove/{memoryId}")
    public ResponseEntity<Map<String, String>> removeMemoryFromPersistentMemory(
            @PathVariable String userId,
            @PathVariable String memoryId) {
        
        log.info("REST request to remove memory {} from persistent memory for user {}", memoryId, userId);
        boolean removed = persistentMemoryService.removeMemoryFromPersistentMemory(userId, memoryId);
        
        if (removed) {
            return ResponseEntity.ok(Map.of("message", "Memory removed from persistent memory"));
        } else {
            return ResponseEntity.badRequest().body(Map.of("message", "Failed to remove memory from persistent memory"));
        }
    }

    /**
     * Get all memory items in persistent memory.
     *
     * @param userId User ID
     * @return List of memory items in persistent memory
     */
    @GetMapping("/{userId}/items")
    public ResponseEntity<List<MemoryItem>> getPersistentMemoryItems(
            @PathVariable String userId) {
        
        log.info("REST request to get persistent memory items for user {}", userId);
        List<MemoryItem> memoryItems = persistentMemoryService.getPersistentMemoryItems(userId);
        return ResponseEntity.ok(memoryItems);
    }

    /**
     * Generate a summary of persistent memory.
     *
     * @param userId User ID
     * @return Generated summary
     */
    @PostMapping("/{userId}/generate-summary")
    public ResponseEntity<Map<String, String>> generatePersistentMemorySummary(
            @PathVariable String userId) {
        
        log.info("REST request to generate persistent memory summary for user {}", userId);
        String summary = persistentMemoryService.generatePersistentMemorySummary(userId);
        return ResponseEntity.ok(Map.of("summary", summary));
    }

    /**
     * Merge two persistent memories.
     *
     * @param sourceUserId Source user ID
     * @param targetUserId Target user ID
     * @return Success message
     */
    @PostMapping("/merge")
    public ResponseEntity<Map<String, String>> mergePersistentMemories(
            @RequestParam String sourceUserId,
            @RequestParam String targetUserId) {
        
        log.info("REST request to merge persistent memories from user {} to user {}", sourceUserId, targetUserId);
        boolean merged = persistentMemoryService.mergePersistentMemories(sourceUserId, targetUserId);
        
        if (merged) {
            return ResponseEntity.ok(Map.of("message", "Persistent memories merged successfully"));
        } else {
            return ResponseEntity.badRequest().body(Map.of("message", "Failed to merge persistent memories"));
        }
    }
}
