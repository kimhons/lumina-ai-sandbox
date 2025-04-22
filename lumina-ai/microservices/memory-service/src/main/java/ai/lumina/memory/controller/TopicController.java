package ai.lumina.memory.controller;

import ai.lumina.memory.model.Topic;
import ai.lumina.memory.model.MemoryItem;
import ai.lumina.memory.service.TopicService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * REST controller for topic management operations.
 */
@RestController
@RequestMapping("/api/memory/topics")
@RequiredArgsConstructor
@Slf4j
public class TopicController {

    private final TopicService topicService;

    /**
     * Get all topics for a user.
     *
     * @param userId User ID
     * @return List of topics
     */
    @GetMapping("/user/{userId}")
    public ResponseEntity<List<Topic>> getTopicsForUser(
            @PathVariable String userId) {
        
        log.info("REST request to get topics for user {}", userId);
        List<Topic> topics = topicService.getTopicsForUser(userId);
        return ResponseEntity.ok(topics);
    }

    /**
     * Get a specific topic by ID.
     *
     * @param topicId Topic ID
     * @return The topic if found
     */
    @GetMapping("/{topicId}")
    public ResponseEntity<Topic> getTopicById(
            @PathVariable String topicId) {
        
        log.info("REST request to get topic {}", topicId);
        Optional<Topic> topic = topicService.getTopicById(topicId);
        
        return topic
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get memories for a specific topic.
     *
     * @param userId User ID
     * @param topicId Topic ID
     * @return List of memory items in the topic
     */
    @GetMapping("/{topicId}/memories")
    public ResponseEntity<List<MemoryItem>> getMemoriesByTopic(
            @RequestParam String userId,
            @PathVariable String topicId) {
        
        log.info("REST request to get memories for topic {} for user {}", topicId, userId);
        List<MemoryItem> memories = topicService.getMemoriesByTopic(userId, topicId);
        return ResponseEntity.ok(memories);
    }

    /**
     * Create a new topic.
     *
     * @param userId User ID
     * @param name Topic name
     * @param description Topic description
     * @return The created topic
     */
    @PostMapping
    public ResponseEntity<Topic> createTopic(
            @RequestParam String userId,
            @RequestParam String name,
            @RequestParam String description) {
        
        log.info("REST request to create topic {} for user {}", name, userId);
        Topic topic = topicService.createTopic(userId, name, description);
        return ResponseEntity.ok(topic);
    }

    /**
     * Update a topic.
     *
     * @param topicId Topic ID
     * @param name New name
     * @param description New description
     * @return The updated topic if found
     */
    @PutMapping("/{topicId}")
    public ResponseEntity<Topic> updateTopic(
            @PathVariable String topicId,
            @RequestParam String name,
            @RequestParam String description) {
        
        log.info("REST request to update topic {}", topicId);
        Optional<Topic> topic = topicService.updateTopic(topicId, name, description);
        
        return topic
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Delete a topic.
     *
     * @param userId User ID
     * @param topicId Topic ID
     * @return Success message
     */
    @DeleteMapping("/{topicId}")
    public ResponseEntity<Map<String, String>> deleteTopic(
            @RequestParam String userId,
            @PathVariable String topicId) {
        
        log.info("REST request to delete topic {} for user {}", topicId, userId);
        boolean deleted = topicService.deleteTopic(userId, topicId);
        
        if (deleted) {
            return ResponseEntity.ok(Map.of("message", "Topic deleted successfully"));
        } else {
            return ResponseEntity.badRequest().body(Map.of("message", "Failed to delete topic"));
        }
    }

    /**
     * Add a memory to a topic.
     *
     * @param topicId Topic ID
     * @param memoryId Memory ID
     * @return Success message
     */
    @PostMapping("/{topicId}/add/{memoryId}")
    public ResponseEntity<Map<String, String>> addMemoryToTopic(
            @PathVariable String topicId,
            @PathVariable String memoryId) {
        
        log.info("REST request to add memory {} to topic {}", memoryId, topicId);
        boolean added = topicService.addMemoryToTopic(topicId, memoryId);
        
        if (added) {
            return ResponseEntity.ok(Map.of("message", "Memory added to topic"));
        } else {
            return ResponseEntity.badRequest().body(Map.of("message", "Failed to add memory to topic"));
        }
    }

    /**
     * Remove a memory from a topic.
     *
     * @param topicId Topic ID
     * @param memoryId Memory ID
     * @return Success message
     */
    @DeleteMapping("/{topicId}/remove/{memoryId}")
    public ResponseEntity<Map<String, String>> removeMemoryFromTopic(
            @PathVariable String topicId,
            @PathVariable String memoryId) {
        
        log.info("REST request to remove memory {} from topic {}", memoryId, topicId);
        boolean removed = topicService.removeMemoryFromTopic(topicId, memoryId);
        
        if (removed) {
            return ResponseEntity.ok(Map.of("message", "Memory removed from topic"));
        } else {
            return ResponseEntity.badRequest().body(Map.of("message", "Failed to remove memory from topic"));
        }
    }

    /**
     * Assign a memory to topics based on content similarity.
     *
     * @param memoryId Memory ID
     * @return Success message
     */
    @PostMapping("/assign/{memoryId}")
    public ResponseEntity<Map<String, String>> assignMemoryToTopics(
            @PathVariable String memoryId) {
        
        log.info("REST request to assign memory {} to topics", memoryId);
        
        // Get the memory item
        Optional<MemoryItem> memoryOpt = Optional.empty(); // This would be retrieved from a repository
        
        if (memoryOpt.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        
        MemoryItem memory = memoryOpt.get();
        topicService.assignMemoryToTopics(memory);
        
        return ResponseEntity.ok(Map.of("message", "Memory assignment to topics initiated"));
    }
}
