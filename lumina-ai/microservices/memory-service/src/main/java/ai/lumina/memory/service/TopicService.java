package ai.lumina.memory.service;

import ai.lumina.memory.model.MemoryItem;
import ai.lumina.memory.model.Topic;
import ai.lumina.memory.repository.MemoryItemRepository;
import ai.lumina.memory.repository.TopicRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service for managing memory topics and hierarchical organization.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class TopicService {

    private final TopicRepository topicRepository;
    private final MemoryItemRepository memoryItemRepository;
    private final CompressionService compressionService;

    /**
     * Get all topics for a user.
     *
     * @param userId The user ID
     * @return List of topics
     */
    public List<Topic> getTopicsForUser(String userId) {
        log.info("Getting topics for user {}", userId);
        return topicRepository.findByUserId(userId);
    }

    /**
     * Get a specific topic by ID.
     *
     * @param topicId The topic ID
     * @return The topic if found, empty otherwise
     */
    public Optional<Topic> getTopicById(String topicId) {
        log.info("Getting topic by ID {}", topicId);
        return topicRepository.findById(topicId);
    }

    /**
     * Get memories for a specific topic.
     *
     * @param userId The user ID
     * @param topicId The topic ID
     * @return List of memory items in the topic
     */
    public List<MemoryItem> getMemoriesByTopic(String userId, String topicId) {
        log.info("Getting memories for topic {} for user {}", topicId, userId);
        
        Optional<Topic> topicOpt = topicRepository.findById(topicId);
        if (topicOpt.isEmpty() || !topicOpt.get().getUserId().equals(userId)) {
            return Collections.emptyList();
        }
        
        Topic topic = topicOpt.get();
        List<String> memoryIds = topic.getMemoryIds();
        
        if (memoryIds == null || memoryIds.isEmpty()) {
            return Collections.emptyList();
        }
        
        return memoryItemRepository.findAllById(memoryIds).stream()
                .filter(item -> item.getUserId().equals(userId))
                .collect(Collectors.toList());
    }

    /**
     * Create a new topic.
     *
     * @param userId The user ID
     * @param name The topic name
     * @param description The topic description
     * @return The created topic
     */
    public Topic createTopic(String userId, String name, String description) {
        log.info("Creating topic {} for user {}", name, userId);
        
        Topic topic = new Topic();
        topic.setUserId(userId);
        topic.setName(name);
        topic.setDescription(description);
        topic.setCreatedAt(LocalDateTime.now());
        topic.setUpdatedAt(LocalDateTime.now());
        topic.setMemoryIds(new ArrayList<>());
        
        return topicRepository.save(topic);
    }

    /**
     * Update a topic.
     *
     * @param topicId The topic ID
     * @param name The new name
     * @param description The new description
     * @return The updated topic if found, empty otherwise
     */
    public Optional<Topic> updateTopic(String topicId, String name, String description) {
        log.info("Updating topic {}", topicId);
        
        Optional<Topic> topicOpt = topicRepository.findById(topicId);
        if (topicOpt.isEmpty()) {
            return Optional.empty();
        }
        
        Topic topic = topicOpt.get();
        topic.setName(name);
        topic.setDescription(description);
        topic.setUpdatedAt(LocalDateTime.now());
        
        return Optional.of(topicRepository.save(topic));
    }

    /**
     * Delete a topic.
     *
     * @param userId The user ID
     * @param topicId The topic ID
     * @return True if deleted, false otherwise
     */
    public boolean deleteTopic(String userId, String topicId) {
        log.info("Deleting topic {} for user {}", topicId, userId);
        
        Optional<Topic> topicOpt = topicRepository.findById(topicId);
        if (topicOpt.isEmpty() || !topicOpt.get().getUserId().equals(userId)) {
            return false;
        }
        
        topicRepository.deleteById(topicId);
        return true;
    }

    /**
     * Add a memory to a topic.
     *
     * @param topicId The topic ID
     * @param memoryId The memory ID
     * @return True if added, false otherwise
     */
    public boolean addMemoryToTopic(String topicId, String memoryId) {
        log.info("Adding memory {} to topic {}", memoryId, topicId);
        
        Optional<Topic> topicOpt = topicRepository.findById(topicId);
        Optional<MemoryItem> memoryOpt = memoryItemRepository.findById(memoryId);
        
        if (topicOpt.isEmpty() || memoryOpt.isEmpty()) {
            return false;
        }
        
        Topic topic = topicOpt.get();
        MemoryItem memory = memoryOpt.get();
        
        if (!topic.getUserId().equals(memory.getUserId())) {
            return false;
        }
        
        List<String> memoryIds = topic.getMemoryIds();
        if (memoryIds == null) {
            memoryIds = new ArrayList<>();
            topic.setMemoryIds(memoryIds);
        }
        
        if (!memoryIds.contains(memoryId)) {
            memoryIds.add(memoryId);
            topic.setUpdatedAt(LocalDateTime.now());
            topicRepository.save(topic);
        }
        
        return true;
    }

    /**
     * Remove a memory from a topic.
     *
     * @param topicId The topic ID
     * @param memoryId The memory ID
     * @return True if removed, false otherwise
     */
    public boolean removeMemoryFromTopic(String topicId, String memoryId) {
        log.info("Removing memory {} from topic {}", memoryId, topicId);
        
        Optional<Topic> topicOpt = topicRepository.findById(topicId);
        if (topicOpt.isEmpty()) {
            return false;
        }
        
        Topic topic = topicOpt.get();
        List<String> memoryIds = topic.getMemoryIds();
        
        if (memoryIds != null && memoryIds.contains(memoryId)) {
            memoryIds.remove(memoryId);
            topic.setUpdatedAt(LocalDateTime.now());
            topicRepository.save(topic);
            return true;
        }
        
        return false;
    }

    /**
     * Assign a memory to topics based on content similarity.
     *
     * @param memory The memory item
     */
    @Async("memoryTaskExecutor")
    public void assignMemoryToTopics(MemoryItem memory) {
        log.info("Assigning memory {} to topics", memory.getId());
        
        String userId = memory.getUserId();
        List<Topic> userTopics = topicRepository.findByUserId(userId);
        
        if (userTopics.isEmpty()) {
            // Create a default topic if none exists
            String topicName = determineTopicName(memory);
            Topic newTopic = createTopic(userId, topicName, "Automatically created topic");
            addMemoryToTopic(newTopic.getId(), memory.getId());
            return;
        }
        
        // Find most similar topics
        Map<Topic, Double> topicSimilarities = new HashMap<>();
        for (Topic topic : userTopics) {
            double similarity = calculateTopicSimilarity(topic, memory);
            topicSimilarities.put(topic, similarity);
        }
        
        // Sort topics by similarity
        List<Map.Entry<Topic, Double>> sortedTopics = topicSimilarities.entrySet().stream()
                .sorted(Map.Entry.<Topic, Double>comparingByValue().reversed())
                .collect(Collectors.toList());
        
        // Add to most similar topic if similarity is above threshold
        if (!sortedTopics.isEmpty() && sortedTopics.get(0).getValue() > 0.5) {
            Topic mostSimilarTopic = sortedTopics.get(0).getKey();
            addMemoryToTopic(mostSimilarTopic.getId(), memory.getId());
        } else {
            // Create a new topic if no similar topics found
            String topicName = determineTopicName(memory);
            Topic newTopic = createTopic(userId, topicName, "Automatically created topic");
            addMemoryToTopic(newTopic.getId(), memory.getId());
        }
    }

    /**
     * Calculate similarity between a topic and a memory item.
     *
     * @param topic The topic
     * @param memory The memory item
     * @return Similarity score (0-1)
     */
    private double calculateTopicSimilarity(Topic topic, MemoryItem memory) {
        // Get memories in the topic
        List<String> memoryIds = topic.getMemoryIds();
        if (memoryIds == null || memoryIds.isEmpty()) {
            return 0.0;
        }
        
        List<MemoryItem> topicMemories = memoryItemRepository.findAllById(memoryIds);
        if (topicMemories.isEmpty()) {
            return 0.0;
        }
        
        // Calculate average similarity
        double totalSimilarity = 0.0;
        for (MemoryItem topicMemory : topicMemories) {
            double similarity = calculateMemorySimilarity(topicMemory, memory);
            totalSimilarity += similarity;
        }
        
        return totalSimilarity / topicMemories.size();
    }

    /**
     * Calculate similarity between two memory items.
     *
     * @param memory1 First memory item
     * @param memory2 Second memory item
     * @return Similarity score (0-1)
     */
    private double calculateMemorySimilarity(MemoryItem memory1, MemoryItem memory2) {
        // Simple implementation using text similarity
        // In a real system, this would use vector embeddings
        String text1 = memory1.getValue();
        String text2 = memory2.getValue();
        
        // Use compression service to get embeddings
        double[] embedding1 = compressionService.getEmbedding(text1);
        double[] embedding2 = compressionService.getEmbedding(text2);
        
        // Calculate cosine similarity
        return cosineSimilarity(embedding1, embedding2);
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
     * Determine a topic name based on memory content.
     *
     * @param memory The memory item
     * @return Generated topic name
     */
    private String determineTopicName(MemoryItem memory) {
        String content = memory.getValue();
        String memoryType = memory.getMemoryType();
        
        // Extract key terms from content
        List<String> keyTerms = extractKeyTerms(content);
        
        if (!keyTerms.isEmpty()) {
            return keyTerms.get(0);
        }
        
        // Fallback to memory type
        return memoryType != null ? memoryType : "General";
    }

    /**
     * Extract key terms from text content.
     *
     * @param content The text content
     * @return List of key terms
     */
    private List<String> extractKeyTerms(String content) {
        // Simple implementation
        // In a real system, this would use NLP techniques
        
        // Remove punctuation and convert to lowercase
        String processed = content.replaceAll("[^a-zA-Z0-9\\s]", "").toLowerCase();
        
        // Split into words
        String[] words = processed.split("\\s+");
        
        // Count word frequencies
        Map<String, Integer> wordCounts = new HashMap<>();
        for (String word : words) {
            if (word.length() > 3 && !isStopWord(word)) {
                wordCounts.put(word, wordCounts.getOrDefault(word, 0) + 1);
            }
        }
        
        // Sort by frequency
        return wordCounts.entrySet().stream()
                .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
                .limit(3)
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
    }

    /**
     * Check if a word is a stop word.
     *
     * @param word The word to check
     * @return True if it's a stop word, false otherwise
     */
    private boolean isStopWord(String word) {
        // Simple list of common stop words
        Set<String> stopWords = Set.of(
                "the", "and", "that", "have", "for", "not", "with", "you", "this", "but",
                "his", "from", "they", "she", "will", "would", "there", "their", "what",
                "about", "which", "when", "make", "like", "time", "just", "know", "take",
                "into", "year", "your", "good", "some", "could", "them", "than", "then",
                "now", "look", "only", "come", "over", "think", "also", "back", "after",
                "use", "two", "how", "our", "work", "first", "well", "way", "even", "new"
        );
        
        return stopWords.contains(word);
    }
}
