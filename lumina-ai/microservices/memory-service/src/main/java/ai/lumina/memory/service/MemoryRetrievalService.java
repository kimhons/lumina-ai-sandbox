package ai.lumina.memory.service;

import ai.lumina.memory.model.MemoryItem;
import ai.lumina.memory.model.UserMemory;
import ai.lumina.memory.repository.MemoryItemRepository;
import ai.lumina.memory.repository.UserMemoryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service for memory retrieval optimization.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class MemoryRetrievalService {

    private final MemoryItemRepository memoryItemRepository;
    private final UserMemoryRepository userMemoryRepository;
    private final CompressionService compressionService;

    /**
     * Retrieve memories based on context.
     *
     * @param userId The user ID
     * @param context The conversation context
     * @param limit Maximum number of memories to retrieve
     * @return List of relevant memory items
     */
    public List<MemoryItem> retrieveByContext(String userId, String context, int limit) {
        log.info("Retrieving memories by context for user {}", userId);
        
        // Get user's memories
        List<MemoryItem> userMemories = memoryItemRepository.findByUserId(userId);
        if (userMemories.isEmpty()) {
            return Collections.emptyList();
        }
        
        // Get embedding for context
        double[] contextEmbedding = compressionService.getEmbedding(context);
        
        // Calculate similarity scores
        Map<MemoryItem, Double> similarityScores = new HashMap<>();
        for (MemoryItem memory : userMemories) {
            double[] memoryEmbedding = compressionService.getEmbedding(memory.getValue());
            double similarity = cosineSimilarity(contextEmbedding, memoryEmbedding);
            similarityScores.put(memory, similarity);
        }
        
        // Sort by similarity and return top results
        return similarityScores.entrySet().stream()
                .sorted(Map.Entry.<MemoryItem, Double>comparingByValue().reversed())
                .limit(limit)
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
    }

    /**
     * Retrieve memories based on query.
     *
     * @param userId The user ID
     * @param query The search query
     * @param limit Maximum number of memories to retrieve
     * @return List of relevant memory items
     */
    public List<MemoryItem> retrieveByQuery(String userId, String query, int limit) {
        log.info("Retrieving memories by query for user {}", userId);
        
        // Get user's memories
        List<MemoryItem> userMemories = memoryItemRepository.findByUserId(userId);
        if (userMemories.isEmpty()) {
            return Collections.emptyList();
        }
        
        // Get embedding for query
        double[] queryEmbedding = compressionService.getEmbedding(query);
        
        // Calculate similarity scores
        Map<MemoryItem, Double> similarityScores = new HashMap<>();
        for (MemoryItem memory : userMemories) {
            double[] memoryEmbedding = compressionService.getEmbedding(memory.getValue());
            double similarity = cosineSimilarity(queryEmbedding, memoryEmbedding);
            similarityScores.put(memory, similarity);
        }
        
        // Sort by similarity and return top results
        return similarityScores.entrySet().stream()
                .sorted(Map.Entry.<MemoryItem, Double>comparingByValue().reversed())
                .limit(limit)
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
    }

    /**
     * Retrieve memories by type.
     *
     * @param userId The user ID
     * @param memoryType The memory type
     * @param limit Maximum number of memories to retrieve
     * @return List of memory items of the specified type
     */
    public List<MemoryItem> retrieveByType(String userId, String memoryType, int limit) {
        log.info("Retrieving memories by type {} for user {}", memoryType, userId);
        
        return memoryItemRepository.findByUserIdAndMemoryType(userId, memoryType)
                .stream()
                .sorted(Comparator.comparing(MemoryItem::getImportanceScore).reversed())
                .limit(limit)
                .collect(Collectors.toList());
    }

    /**
     * Optimize retrieval strategy based on inputs.
     *
     * @param userId The user ID
     * @param context The conversation context
     * @param query The search query (optional)
     * @param memoryType The memory type (optional)
     * @param limit Maximum number of memories to retrieve
     * @return List of relevant memory items
     */
    public List<MemoryItem> optimizeRetrievalStrategy(String userId, String context, 
                                                    String query, String memoryType, int limit) {
        log.info("Optimizing retrieval strategy for user {}", userId);
        
        // Determine the best retrieval strategy
        if (query != null && !query.isEmpty()) {
            // If explicit query is provided, prioritize query-based retrieval
            return retrieveByQuery(userId, query, limit);
        } else if (memoryType != null && !memoryType.isEmpty()) {
            // If memory type is specified, filter by type
            List<MemoryItem> typeMemories = retrieveByType(userId, memoryType, limit);
            
            // If context is provided, re-rank by context relevance
            if (context != null && !context.isEmpty() && !typeMemories.isEmpty()) {
                double[] contextEmbedding = compressionService.getEmbedding(context);
                
                // Calculate similarity scores
                Map<MemoryItem, Double> similarityScores = new HashMap<>();
                for (MemoryItem memory : typeMemories) {
                    double[] memoryEmbedding = compressionService.getEmbedding(memory.getValue());
                    double similarity = cosineSimilarity(contextEmbedding, memoryEmbedding);
                    similarityScores.put(memory, similarity);
                }
                
                // Sort by similarity
                return similarityScores.entrySet().stream()
                        .sorted(Map.Entry.<MemoryItem, Double>comparingByValue().reversed())
                        .map(Map.Entry::getKey)
                        .collect(Collectors.toList());
            }
            
            return typeMemories;
        } else if (context != null && !context.isEmpty()) {
            // If only context is provided, use context-based retrieval
            return retrieveByContext(userId, context, limit);
        } else {
            // Fallback to retrieving most important memories
            return memoryItemRepository.findByUserId(userId)
                    .stream()
                    .sorted(Comparator.comparing(MemoryItem::getImportanceScore).reversed())
                    .limit(limit)
                    .collect(Collectors.toList());
        }
    }

    /**
     * Get diverse memories for a user.
     *
     * @param userId The user ID
     * @param limit Maximum number of memories to retrieve
     * @return List of diverse memory items
     */
    public List<MemoryItem> getDiverseMemories(String userId, int limit) {
        log.info("Getting diverse memories for user {}", userId);
        
        // Get user's memories
        List<MemoryItem> userMemories = memoryItemRepository.findByUserId(userId);
        if (userMemories.isEmpty() || userMemories.size() <= limit) {
            return userMemories;
        }
        
        // Sort by importance
        List<MemoryItem> sortedMemories = userMemories.stream()
                .sorted(Comparator.comparing(MemoryItem::getImportanceScore).reversed())
                .collect(Collectors.toList());
        
        // Always include the most important memory
        List<MemoryItem> result = new ArrayList<>();
        result.add(sortedMemories.get(0));
        sortedMemories.remove(0);
        
        // Add diverse memories
        while (result.size() < limit && !sortedMemories.isEmpty()) {
            // Find the memory that is most different from the current result set
            MemoryItem mostDiverse = findMostDiverseMemory(result, sortedMemories);
            result.add(mostDiverse);
            sortedMemories.remove(mostDiverse);
        }
        
        return result;
    }

    /**
     * Find the memory that is most different from a set of memories.
     *
     * @param currentSet Current set of memories
     * @param candidates Candidate memories
     * @return The most diverse memory
     */
    private MemoryItem findMostDiverseMemory(List<MemoryItem> currentSet, List<MemoryItem> candidates) {
        MemoryItem mostDiverse = null;
        double maxMinDistance = -1.0;
        
        for (MemoryItem candidate : candidates) {
            double minDistance = Double.MAX_VALUE;
            
            // Calculate minimum distance to any memory in the current set
            for (MemoryItem current : currentSet) {
                double[] candidateEmbedding = compressionService.getEmbedding(candidate.getValue());
                double[] currentEmbedding = compressionService.getEmbedding(current.getValue());
                
                double similarity = cosineSimilarity(candidateEmbedding, currentEmbedding);
                double distance = 1.0 - similarity;
                
                minDistance = Math.min(minDistance, distance);
            }
            
            // Update most diverse if this candidate has a larger minimum distance
            if (minDistance > maxMinDistance) {
                maxMinDistance = minDistance;
                mostDiverse = candidate;
            }
        }
        
        return mostDiverse;
    }

    /**
     * Calculate cosine similarity between two vectors.
     *
     * @param vector1 First vector
     * @param vector2 Second vector
     * @return Cosine similarity (0-1)
     */
    private double cosineSimilarity(double[] vector1, double[] vector2) {
        if (vector1.length != vector2.length) {
            return 0.0;
        }
        
        double dotProduct = 0.0;
        double norm1 = 0.0;
        double norm2 = 0.0;
        
        for (int i = 0; i < vector1.length; i++) {
            dotProduct += vector1[i] * vector2[i];
            norm1 += Math.pow(vector1[i], 2);
            norm2 += Math.pow(vector2[i], 2);
        }
        
        if (norm1 == 0.0 || norm2 == 0.0) {
            return 0.0;
        }
        
        return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
    }

    /**
     * Update memory access statistics.
     *
     * @param memoryId The memory ID
     */
    public void updateMemoryAccess(String memoryId) {
        log.info("Updating memory access for memory {}", memoryId);
        
        Optional<MemoryItem> memoryOpt = memoryItemRepository.findById(memoryId);
        if (memoryOpt.isPresent()) {
            MemoryItem memory = memoryOpt.get();
            memory.setLastAccessedAt(LocalDateTime.now());
            memory.setAccessCount(memory.getAccessCount() + 1);
            memoryItemRepository.save(memory);
        }
    }

    /**
     * Scheduled task to update memory importance scores based on access patterns.
     */
    @Scheduled(cron = "0 0 * * * *") // Run every hour
    public void updateMemoryImportance() {
        log.info("Running scheduled task to update memory importance scores");
        
        List<MemoryItem> allMemories = memoryItemRepository.findAll();
        LocalDateTime now = LocalDateTime.now();
        
        for (MemoryItem memory : allMemories) {
            // Skip memories without access data
            if (memory.getLastAccessedAt() == null) {
                continue;
            }
            
            // Calculate recency factor (0-1)
            long daysSinceAccess = java.time.Duration.between(memory.getLastAccessedAt(), now).toDays();
            double recencyFactor = Math.exp(-0.1 * daysSinceAccess); // Exponential decay
            
            // Calculate frequency factor (0-1)
            double frequencyFactor = Math.min(1.0, memory.getAccessCount() / 10.0);
            
            // Update importance score (weighted average with original score)
            double originalScore = memory.getImportanceScore();
            double newScore = 0.6 * originalScore + 0.2 * recencyFactor + 0.2 * frequencyFactor;
            
            // Ensure score is in range [0,1]
            newScore = Math.max(0.0, Math.min(1.0, newScore));
            
            // Update if score changed significantly
            if (Math.abs(newScore - originalScore) > 0.05) {
                memory.setImportanceScore(newScore);
                memoryItemRepository.save(memory);
                log.debug("Updated importance score for memory {}: {} -> {}", 
                         memory.getId(), originalScore, newScore);
            }
        }
    }
}
