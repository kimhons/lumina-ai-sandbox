package ai.lumina.collaboration.service;

import ai.lumina.collaboration.model.ContextItem;
import ai.lumina.collaboration.repository.ContextItemRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

/**
 * Service for managing context items in the collaboration system.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ContextManagerService {

    private final ContextItemRepository contextItemRepository;
    private final ObjectMapper objectMapper;

    /**
     * Share context with the collaboration system.
     *
     * @param key the context key
     * @param value the context value
     * @param contextType the context type
     * @param scope the context scope
     * @param scopeId the scope ID
     * @param agentId the agent ID
     * @param expiresAt optional expiration time
     * @return the created context item
     * @throws JsonProcessingException if value cannot be serialized to JSON
     */
    @Transactional
    public ContextItem shareContext(
            String key,
            Object value,
            ContextItem.ContextType contextType,
            ContextItem.ContextScope scope,
            String scopeId,
            String agentId,
            LocalDateTime expiresAt) throws JsonProcessingException {
        
        log.info("Sharing context: {} for {}/{}", key, scope, scopeId);
        
        // Convert value to JSON
        String valueJson = objectMapper.writeValueAsString(value);
        
        // Create context item
        String contextId = UUID.randomUUID().toString();
        ContextItem contextItem = ContextItem.builder()
                .contextId(contextId)
                .key(key)
                .valueJson(valueJson)
                .contextType(contextType)
                .scope(scope)
                .scopeId(scopeId)
                .agentId(agentId)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .expiresAt(expiresAt)
                .build();
        
        return contextItemRepository.save(contextItem);
    }

    /**
     * Get a context item by ID.
     *
     * @param contextId the context ID
     * @return the context item, or empty if not found
     */
    @Transactional(readOnly = true)
    public Optional<ContextItem> getContext(String contextId) {
        return contextItemRepository.findByContextId(contextId);
    }

    /**
     * Get context items by key.
     *
     * @param key the context key
     * @return list of context items
     */
    @Transactional(readOnly = true)
    public List<ContextItem> getContextByKey(String key) {
        return contextItemRepository.findByKey(key);
    }

    /**
     * Get context items by scope and scope ID.
     *
     * @param scope the context scope
     * @param scopeId the scope ID
     * @return list of context items
     */
    @Transactional(readOnly = true)
    public List<ContextItem> getContextByScope(ContextItem.ContextScope scope, String scopeId) {
        return contextItemRepository.findByScopeAndScopeId(scope, scopeId);
    }

    /**
     * Get context items by scope, scope ID, and context type.
     *
     * @param scope the context scope
     * @param scopeId the scope ID
     * @param contextType the context type
     * @return list of context items
     */
    @Transactional(readOnly = true)
    public List<ContextItem> getContextByTypeAndScope(
            ContextItem.ContextScope scope, 
            String scopeId, 
            ContextItem.ContextType contextType) {
        return contextItemRepository.findByScopeAndScopeIdAndContextType(scope, scopeId, contextType);
    }

    /**
     * Get context items accessible to an agent.
     *
     * @param agentId the agent ID
     * @return list of context items
     */
    @Transactional(readOnly = true)
    public List<ContextItem> getContextAccessibleToAgent(String agentId) {
        return contextItemRepository.findAccessibleToAgent(agentId);
    }

    /**
     * Update a context item's value.
     *
     * @param contextId the context ID
     * @param value the new value
     * @return the updated context item, or empty if not found
     * @throws JsonProcessingException if value cannot be serialized to JSON
     */
    @Transactional
    public Optional<ContextItem> updateContextValue(String contextId, Object value) throws JsonProcessingException {
        Optional<ContextItem> contextOpt = contextItemRepository.findByContextId(contextId);
        if (contextOpt.isPresent()) {
            ContextItem context = contextOpt.get();
            
            // Convert value to JSON
            String valueJson = objectMapper.writeValueAsString(value);
            
            context.setValueJson(valueJson);
            context.setUpdatedAt(LocalDateTime.now());
            
            return Optional.of(contextItemRepository.save(context));
        }
        return Optional.empty();
    }

    /**
     * Delete a context item.
     *
     * @param contextId the context ID
     * @return true if context was deleted, false if not found
     */
    @Transactional
    public boolean deleteContext(String contextId) {
        Optional<ContextItem> contextOpt = contextItemRepository.findByContextId(contextId);
        if (contextOpt.isPresent()) {
            contextItemRepository.delete(contextOpt.get());
            log.info("Deleted context: {}", contextId);
            return true;
        }
        return false;
    }

    /**
     * Get the value of a context item as a specific type.
     *
     * @param contextId the context ID
     * @param valueType the class of the value type
     * @param <T> the value type
     * @return the value, or empty if not found or cannot be converted
     */
    @Transactional(readOnly = true)
    public <T> Optional<T> getContextValue(String contextId, Class<T> valueType) {
        Optional<ContextItem> contextOpt = contextItemRepository.findByContextId(contextId);
        if (contextOpt.isPresent()) {
            ContextItem context = contextOpt.get();
            try {
                T value = objectMapper.readValue(context.getValueJson(), valueType);
                return Optional.of(value);
            } catch (JsonProcessingException e) {
                log.error("Failed to deserialize context value: {}", e.getMessage());
                return Optional.empty();
            }
        }
        return Optional.empty();
    }

    /**
     * Clean up expired context items.
     *
     * @return number of items deleted
     */
    @Transactional
    public int cleanupExpiredContext() {
        LocalDateTime now = LocalDateTime.now();
        List<ContextItem> expiredItems = contextItemRepository.findByExpiresAtIsNullOrExpiresAtGreaterThan(now);
        
        int count = 0;
        for (ContextItem item : expiredItems) {
            contextItemRepository.delete(item);
            count++;
        }
        
        log.info("Cleaned up {} expired context items", count);
        return count;
    }
}
