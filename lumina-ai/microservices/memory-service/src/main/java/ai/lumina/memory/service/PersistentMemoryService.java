package ai.lumina.memory.service;

import ai.lumina.memory.model.PersistentMemory;
import ai.lumina.memory.model.MemoryItem;
import ai.lumina.memory.repository.PersistentMemoryRepository;
import ai.lumina.memory.repository.MemoryItemRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service for managing cross-session persistent memory.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class PersistentMemoryService {

    private final PersistentMemoryRepository persistentMemoryRepository;
    private final MemoryItemRepository memoryItemRepository;
    private final CompressionService compressionService;

    /**
     * Get persistent memory for a user.
     *
     * @param userId The user ID
     * @return The persistent memory if found, empty otherwise
     */
    public Optional<PersistentMemory> getPersistentMemory(String userId) {
        log.info("Getting persistent memory for user {}", userId);
        return persistentMemoryRepository.findByUserId(userId);
    }

    /**
     * Create or update persistent memory for a user.
     *
     * @param userId The user ID
     * @param summary The memory summary
     * @return The created or updated persistent memory
     */
    public PersistentMemory createOrUpdatePersistentMemory(String userId, String summary) {
        log.info("Creating or updating persistent memory for user {}", userId);
        
        Optional<PersistentMemory> existingMemory = persistentMemoryRepository.findByUserId(userId);
        
        if (existingMemory.isPresent()) {
            PersistentMemory memory = existingMemory.get();
            memory.setSummary(summary);
            memory.setUpdatedAt(LocalDateTime.now());
            return persistentMemoryRepository.save(memory);
        } else {
            PersistentMemory memory = new PersistentMemory();
            memory.setUserId(userId);
            memory.setSummary(summary);
            memory.setCreatedAt(LocalDateTime.now());
            memory.setUpdatedAt(LocalDateTime.now());
            return persistentMemoryRepository.save(memory);
        }
    }

    /**
     * Add a memory item to persistent memory.
     *
     * @param userId The user ID
     * @param memoryId The memory item ID
     * @return True if added, false otherwise
     */
    public boolean addMemoryToPersistentMemory(String userId, String memoryId) {
        log.info("Adding memory {} to persistent memory for user {}", memoryId, userId);
        
        Optional<MemoryItem> memoryOpt = memoryItemRepository.findById(memoryId);
        if (memoryOpt.isEmpty() || !memoryOpt.get().getUserId().equals(userId)) {
            return false;
        }
        
        Optional<PersistentMemory> persistentMemoryOpt = persistentMemoryRepository.findByUserId(userId);
        PersistentMemory persistentMemory;
        
        if (persistentMemoryOpt.isPresent()) {
            persistentMemory = persistentMemoryOpt.get();
        } else {
            persistentMemory = new PersistentMemory();
            persistentMemory.setUserId(userId);
            persistentMemory.setSummary("");
            persistentMemory.setCreatedAt(LocalDateTime.now());
            persistentMemory.setMemoryIds(new ArrayList<>());
        }
        
        List<String> memoryIds = persistentMemory.getMemoryIds();
        if (memoryIds == null) {
            memoryIds = new ArrayList<>();
            persistentMemory.setMemoryIds(memoryIds);
        }
        
        if (!memoryIds.contains(memoryId)) {
            memoryIds.add(memoryId);
            persistentMemory.setUpdatedAt(LocalDateTime.now());
            persistentMemoryRepository.save(persistentMemory);
            return true;
        }
        
        return false;
    }

    /**
     * Remove a memory item from persistent memory.
     *
     * @param userId The user ID
     * @param memoryId The memory item ID
     * @return True if removed, false otherwise
     */
    public boolean removeMemoryFromPersistentMemory(String userId, String memoryId) {
        log.info("Removing memory {} from persistent memory for user {}", memoryId, userId);
        
        Optional<PersistentMemory> persistentMemoryOpt = persistentMemoryRepository.findByUserId(userId);
        if (persistentMemoryOpt.isEmpty()) {
            return false;
        }
        
        PersistentMemory persistentMemory = persistentMemoryOpt.get();
        List<String> memoryIds = persistentMemory.getMemoryIds();
        
        if (memoryIds != null && memoryIds.contains(memoryId)) {
            memoryIds.remove(memoryId);
            persistentMemory.setUpdatedAt(LocalDateTime.now());
            persistentMemoryRepository.save(persistentMemory);
            return true;
        }
        
        return false;
    }

    /**
     * Get all memory items in persistent memory.
     *
     * @param userId The user ID
     * @return List of memory items in persistent memory
     */
    public List<MemoryItem> getPersistentMemoryItems(String userId) {
        log.info("Getting persistent memory items for user {}", userId);
        
        Optional<PersistentMemory> persistentMemoryOpt = persistentMemoryRepository.findByUserId(userId);
        if (persistentMemoryOpt.isEmpty()) {
            return Collections.emptyList();
        }
        
        PersistentMemory persistentMemory = persistentMemoryOpt.get();
        List<String> memoryIds = persistentMemory.getMemoryIds();
        
        if (memoryIds == null || memoryIds.isEmpty()) {
            return Collections.emptyList();
        }
        
        return memoryItemRepository.findAllById(memoryIds);
    }

    /**
     * Generate a summary of persistent memory.
     *
     * @param userId The user ID
     * @return Generated summary
     */
    public String generatePersistentMemorySummary(String userId) {
        log.info("Generating persistent memory summary for user {}", userId);
        
        List<MemoryItem> memoryItems = getPersistentMemoryItems(userId);
        if (memoryItems.isEmpty()) {
            return "";
        }
        
        // Sort by importance
        memoryItems.sort(Comparator.comparing(MemoryItem::getImportanceScore).reversed());
        
        // Concatenate memory values
        StringBuilder content = new StringBuilder();
        for (MemoryItem item : memoryItems) {
            content.append(item.getValue()).append("\n\n");
        }
        
        // Compress to create summary
        String summary = compressionService.compressText(content.toString(), 0.3);
        
        // Update persistent memory with summary
        createOrUpdatePersistentMemory(userId, summary);
        
        return summary;
    }

    /**
     * Scheduled task to update persistent memory summaries.
     */
    @Scheduled(cron = "0 0 3 * * *") // Run at 3 AM every day
    public void updatePersistentMemorySummaries() {
        log.info("Running scheduled task to update persistent memory summaries");
        
        List<PersistentMemory> allPersistentMemories = persistentMemoryRepository.findAll();
        
        for (PersistentMemory persistentMemory : allPersistentMemories) {
            try {
                String userId = persistentMemory.getUserId();
                generatePersistentMemorySummary(userId);
                log.debug("Updated persistent memory summary for user {}", userId);
            } catch (Exception e) {
                log.error("Error updating persistent memory summary: {}", e.getMessage(), e);
            }
        }
    }

    /**
     * Merge two persistent memories (e.g., when merging user accounts).
     *
     * @param sourceUserId Source user ID
     * @param targetUserId Target user ID
     * @return True if merged successfully, false otherwise
     */
    public boolean mergePersistentMemories(String sourceUserId, String targetUserId) {
        log.info("Merging persistent memories from user {} to user {}", sourceUserId, targetUserId);
        
        Optional<PersistentMemory> sourceMemoryOpt = persistentMemoryRepository.findByUserId(sourceUserId);
        if (sourceMemoryOpt.isEmpty()) {
            return false;
        }
        
        PersistentMemory sourceMemory = sourceMemoryOpt.get();
        List<String> sourceMemoryIds = sourceMemory.getMemoryIds();
        
        if (sourceMemoryIds == null || sourceMemoryIds.isEmpty()) {
            return false;
        }
        
        Optional<PersistentMemory> targetMemoryOpt = persistentMemoryRepository.findByUserId(targetUserId);
        PersistentMemory targetMemory;
        
        if (targetMemoryOpt.isPresent()) {
            targetMemory = targetMemoryOpt.get();
        } else {
            targetMemory = new PersistentMemory();
            targetMemory.setUserId(targetUserId);
            targetMemory.setSummary("");
            targetMemory.setCreatedAt(LocalDateTime.now());
            targetMemory.setMemoryIds(new ArrayList<>());
        }
        
        List<String> targetMemoryIds = targetMemory.getMemoryIds();
        if (targetMemoryIds == null) {
            targetMemoryIds = new ArrayList<>();
            targetMemory.setMemoryIds(targetMemoryIds);
        }
        
        // Add source memory IDs to target
        boolean changed = false;
        for (String memoryId : sourceMemoryIds) {
            if (!targetMemoryIds.contains(memoryId)) {
                targetMemoryIds.add(memoryId);
                changed = true;
            }
        }
        
        if (changed) {
            targetMemory.setUpdatedAt(LocalDateTime.now());
            persistentMemoryRepository.save(targetMemory);
            
            // Generate new summary
            generatePersistentMemorySummary(targetUserId);
        }
        
        return true;
    }
}
