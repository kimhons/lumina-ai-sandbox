package ai.lumina.collaboration.service;

import ai.lumina.collaboration.model.MemoryItem;
import ai.lumina.collaboration.repository.MemoryItemRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

/**
 * Service for managing memory items in the collaboration system.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class SharedMemoryService {

    private final MemoryItemRepository memoryItemRepository;
    private final ObjectMapper objectMapper;

    /**
     * Create a new memory item.
     *
     * @param key the memory key
     * @param value the memory value
     * @param memoryType the memory type
     * @param scope the memory scope
     * @param scopeId the scope ID
     * @param agentId the agent ID
     * @param importance the importance (0.0 to 1.0)
     * @param tags optional tags
     * @return the created memory item
     * @throws JsonProcessingException if value cannot be serialized to JSON
     */
    @Transactional
    public MemoryItem createMemory(
            String key,
            Object value,
            MemoryItem.MemoryType memoryType,
            MemoryItem.MemoryScope scope,
            String scopeId,
            String agentId,
            Float importance,
            Set<String> tags) throws JsonProcessingException {
        
        log.info("Creating memory: {} for {}/{}", key, scope, scopeId);
        
        // Convert value to JSON
        String valueJson = objectMapper.writeValueAsString(value);
        
        // Create memory item
        String memoryId = UUID.randomUUID().toString();
        LocalDateTime now = LocalDateTime.now();
        
        MemoryItem memoryItem = MemoryItem.builder()
                .memoryId(memoryId)
                .key(key)
                .valueJson(valueJson)
                .memoryType(memoryType)
                .scope(scope)
                .scopeId(scopeId)
                .agentId(agentId)
                .importance(importance)
                .tags(tags != null ? tags : new HashSet<>())
                .createdAt(now)
                .updatedAt(now)
                .accessedAt(now)
                .accessCount(0)
                .build();
        
        return memoryItemRepository.save(memoryItem);
    }

    /**
     * Get a memory item by ID.
     *
     * @param memoryId the memory ID
     * @return the memory item, or empty if not found
     */
    @Transactional
    public Optional<MemoryItem> getMemory(String memoryId) {
        Optional<MemoryItem> memoryOpt = memoryItemRepository.findByMemoryId(memoryId);
        
        // Update access information
        if (memoryOpt.isPresent()) {
            MemoryItem memory = memoryOpt.get();
            memory.setAccessedAt(LocalDateTime.now());
            memory.setAccessCount(memory.getAccessCount() + 1);
            return Optional.of(memoryItemRepository.save(memory));
        }
        
        return Optional.empty();
    }

    /**
     * Get memory items by key.
     *
     * @param key the memory key
     * @return list of memory items
     */
    @Transactional(readOnly = true)
    public List<MemoryItem> getMemoriesByKey(String key) {
        return memoryItemRepository.findByKey(key);
    }

    /**
     * Get memory items by scope and scope ID.
     *
     * @param scope the memory scope
     * @param scopeId the scope ID
     * @return list of memory items
     */
    @Transactional(readOnly = true)
    public List<MemoryItem> getMemoriesByScope(MemoryItem.MemoryScope scope, String scopeId) {
        return memoryItemRepository.findByScopeAndScopeId(scope, scopeId);
    }

    /**
     * Get memory items by memory type.
     *
     * @param memoryType the memory type
     * @return list of memory items
     */
    @Transactional(readOnly = true)
    public List<MemoryItem> getMemoriesByType(MemoryItem.MemoryType memoryType) {
        return memoryItemRepository.findByMemoryType(memoryType);
    }

    /**
     * Get memory items by tag.
     *
     * @param tag the tag
     * @return list of memory items
     */
    @Transactional(readOnly = true)
    public List<MemoryItem> getMemoriesByTag(String tag) {
        return memoryItemRepository.findByTag(tag);
    }

    /**
     * Get memory items by multiple tags (must have all tags).
     *
     * @param tags the set of tags
     * @return list of memory items
     */
    @Transactional(readOnly = true)
    public List<MemoryItem> getMemoriesByAllTags(Set<String> tags) {
        if (tags.isEmpty()) {
            return Collections.emptyList();
        }
        return memoryItemRepository.findByAllTags(tags, tags.size());
    }

    /**
     * Get memory items by multiple tags (must have at least one tag).
     *
     * @param tags the set of tags
     * @return list of memory items
     */
    @Transactional(readOnly = true)
    public List<MemoryItem> getMemoriesByAnyTag(Set<String> tags) {
        if (tags.isEmpty()) {
            return Collections.emptyList();
        }
        return memoryItemRepository.findByAnyTag(tags);
    }

    /**
     * Get memory items accessible to an agent.
     *
     * @param agentId the agent ID
     * @return list of memory items
     */
    @Transactional(readOnly = true)
    public List<MemoryItem> getMemoriesAccessibleToAgent(String agentId) {
        return memoryItemRepository.findAccessibleToAgent(agentId);
    }

    /**
     * Update a memory item's value.
     *
     * @param memoryId the memory ID
     * @param value the new value
     * @return the updated memory item, or empty if not found
     * @throws JsonProcessingException if value cannot be serialized to JSON
     */
    @Transactional
    public Optional<MemoryItem> updateMemoryValue(String memoryId, Object value) throws JsonProcessingException {
        Optional<MemoryItem> memoryOpt = memoryItemRepository.findByMemoryId(memoryId);
        if (memoryOpt.isPresent()) {
            MemoryItem memory = memoryOpt.get();
            
            // Convert value to JSON
            String valueJson = objectMapper.writeValueAsString(value);
            
            memory.setValueJson(valueJson);
            memory.setUpdatedAt(LocalDateTime.now());
            
            return Optional.of(memoryItemRepository.save(memory));
        }
        return Optional.empty();
    }

    /**
     * Update a memory item's importance.
     *
     * @param memoryId the memory ID
     * @param importance the new importance
     * @return the updated memory item, or empty if not found
     */
    @Transactional
    public Optional<MemoryItem> updateMemoryImportance(String memoryId, Float importance) {
        Optional<MemoryItem> memoryOpt = memoryItemRepository.findByMemoryId(memoryId);
        if (memoryOpt.isPresent()) {
            MemoryItem memory = memoryOpt.get();
            memory.setImportance(importance);
            memory.setUpdatedAt(LocalDateTime.now());
            return Optional.of(memoryItemRepository.save(memory));
        }
        return Optional.empty();
    }

    /**
     * Update a memory item's tags.
     *
     * @param memoryId the memory ID
     * @param tags the new tags
     * @return the updated memory item, or empty if not found
     */
    @Transactional
    public Optional<MemoryItem> updateMemoryTags(String memoryId, Set<String> tags) {
        Optional<MemoryItem> memoryOpt = memoryItemRepository.findByMemoryId(memoryId);
        if (memoryOpt.isPresent()) {
            MemoryItem memory = memoryOpt.get();
            memory.setTags(tags);
            memory.setUpdatedAt(LocalDateTime.now());
            return Optional.of(memoryItemRepository.save(memory));
        }
        return Optional.empty();
    }

    /**
     * Delete a memory item.
     *
     * @param memoryId the memory ID
     * @return true if memory was deleted, false if not found
     */
    @Transactional
    public boolean deleteMemory(String memoryId) {
        Optional<MemoryItem> memoryOpt = memoryItemRepository.findByMemoryId(memoryId);
        if (memoryOpt.isPresent()) {
            memoryItemRepository.delete(memoryOpt.get());
            log.info("Deleted memory: {}", memoryId);
            return true;
        }
        return false;
    }

    /**
     * Get the value of a memory item as a specific type.
     *
     * @param memoryId the memory ID
     * @param valueType the class of the value type
     * @param <T> the value type
     * @return the value, or empty if not found or cannot be converted
     */
    @Transactional
    public <T> Optional<T> getMemoryValue(String memoryId, Class<T> valueType) {
        Optional<MemoryItem> memoryOpt = getMemory(memoryId);
        if (memoryOpt.isPresent()) {
            MemoryItem memory = memoryOpt.get();
            try {
                T value = objectMapper.readValue(memory.getValueJson(), valueType);
                return Optional.of(value);
            } catch (JsonProcessingException e) {
                log.error("Failed to deserialize memory value: {}", e.getMessage());
                return Optional.empty();
            }
        }
        return Optional.empty();
    }

    /**
     * Find memories with importance above a threshold.
     *
     * @param minImportance the minimum importance
     * @return list of memory items
     */
    @Transactional(readOnly = true)
    public List<MemoryItem> findImportantMemories(Float minImportance) {
        return memoryItemRepository.findByImportanceGreaterThanEqual(minImportance);
    }

    /**
     * Find frequently accessed memories.
     *
     * @param minAccessCount the minimum access count
     * @return list of memory items
     */
    @Transactional(readOnly = true)
    public List<MemoryItem> findFrequentlyAccessedMemories(Integer minAccessCount) {
        return memoryItemRepository.findByAccessCountGreaterThanEqual(minAccessCount);
    }

    /**
     * Find recently accessed memories.
     *
     * @param since the time threshold
     * @return list of memory items
     */
    @Transactional(readOnly = true)
    public List<MemoryItem> findRecentlyAccessedMemories(LocalDateTime since) {
        return memoryItemRepository.findByAccessedAtGreaterThan(since);
    }
}
