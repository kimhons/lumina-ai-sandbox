package ai.lumina.collaboration.controller;

import ai.lumina.collaboration.model.LearningEvent;
import ai.lumina.collaboration.service.CollaborativeLearningService;
import com.fasterxml.jackson.core.JsonProcessingException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;

/**
 * REST controller for managing collaborative learning events in the collaboration system.
 */
@RestController
@RequestMapping("/api/v1/collaboration/learning")
@RequiredArgsConstructor
@Slf4j
public class CollaborativeLearningController {

    private final CollaborativeLearningService learningService;

    /**
     * Record a new learning event.
     *
     * @param request the learning event recording request
     * @return the created learning event
     */
    @PostMapping
    public ResponseEntity<LearningEvent> recordLearningEvent(@RequestBody LearningEventRequest request) {
        log.info("Received request to record learning event of type {} by {}", 
                request.getEventType(), request.getAgentId());
        
        try {
            LearningEvent learningEvent = learningService.recordLearningEvent(
                    request.getEventType(),
                    request.getAgentId(),
                    request.getTaskId(),
                    request.getTeamId(),
                    request.getContent(),
                    request.getImportance(),
                    request.getRelatedEvents()
            );
            
            return ResponseEntity.status(HttpStatus.CREATED).body(learningEvent);
        } catch (JsonProcessingException e) {
            log.error("Failed to serialize learning event content: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }

    /**
     * Get a learning event by ID.
     *
     * @param eventId the event ID
     * @return the learning event, or 404 if not found
     */
    @GetMapping("/{eventId}")
    public ResponseEntity<LearningEvent> getLearningEvent(@PathVariable String eventId) {
        log.info("Received request to get learning event: {}", eventId);
        
        return learningService.getLearningEvent(eventId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get learning events by type.
     *
     * @param eventType the event type
     * @return list of learning events
     */
    @GetMapping("/by-type")
    public ResponseEntity<List<LearningEvent>> getLearningEventsByType(
            @RequestParam LearningEvent.LearningEventType eventType) {
        
        log.info("Received request to get learning events by type: {}", eventType);
        
        List<LearningEvent> events = learningService.getLearningEventsByType(eventType);
        return ResponseEntity.ok(events);
    }

    /**
     * Get learning events by agent.
     *
     * @param agentId the agent ID
     * @return list of learning events
     */
    @GetMapping("/by-agent/{agentId}")
    public ResponseEntity<List<LearningEvent>> getLearningEventsByAgent(@PathVariable String agentId) {
        log.info("Received request to get learning events by agent: {}", agentId);
        
        List<LearningEvent> events = learningService.getLearningEventsByAgent(agentId);
        return ResponseEntity.ok(events);
    }

    /**
     * Get learning events by task.
     *
     * @param taskId the task ID
     * @return list of learning events
     */
    @GetMapping("/by-task/{taskId}")
    public ResponseEntity<List<LearningEvent>> getLearningEventsByTask(@PathVariable String taskId) {
        log.info("Received request to get learning events by task: {}", taskId);
        
        List<LearningEvent> events = learningService.getLearningEventsByTask(taskId);
        return ResponseEntity.ok(events);
    }

    /**
     * Get learning events by team.
     *
     * @param teamId the team ID
     * @return list of learning events
     */
    @GetMapping("/by-team/{teamId}")
    public ResponseEntity<List<LearningEvent>> getLearningEventsByTeam(@PathVariable String teamId) {
        log.info("Received request to get learning events by team: {}", teamId);
        
        List<LearningEvent> events = learningService.getLearningEventsByTeam(teamId);
        return ResponseEntity.ok(events);
    }

    /**
     * Get learning events by agent and type.
     *
     * @param agentId the agent ID
     * @param eventType the event type
     * @return list of learning events
     */
    @GetMapping("/by-agent-and-type")
    public ResponseEntity<List<LearningEvent>> getLearningEventsByAgentAndType(
            @RequestParam String agentId,
            @RequestParam LearningEvent.LearningEventType eventType) {
        
        log.info("Received request to get learning events by agent: {} and type: {}", agentId, eventType);
        
        List<LearningEvent> events = learningService.getLearningEventsByAgentAndType(agentId, eventType);
        return ResponseEntity.ok(events);
    }

    /**
     * Get learning events by team and type.
     *
     * @param teamId the team ID
     * @param eventType the event type
     * @return list of learning events
     */
    @GetMapping("/by-team-and-type")
    public ResponseEntity<List<LearningEvent>> getLearningEventsByTeamAndType(
            @RequestParam String teamId,
            @RequestParam LearningEvent.LearningEventType eventType) {
        
        log.info("Received request to get learning events by team: {} and type: {}", teamId, eventType);
        
        List<LearningEvent> events = learningService.getLearningEventsByTeamAndType(teamId, eventType);
        return ResponseEntity.ok(events);
    }

    /**
     * Get learning events related to a specific event.
     *
     * @param eventId the related event ID
     * @return list of learning events
     */
    @GetMapping("/related-to/{eventId}")
    public ResponseEntity<List<LearningEvent>> getRelatedLearningEvents(@PathVariable String eventId) {
        log.info("Received request to get learning events related to: {}", eventId);
        
        List<LearningEvent> events = learningService.getRelatedLearningEvents(eventId);
        return ResponseEntity.ok(events);
    }

    /**
     * Get learning events accessible to an agent.
     *
     * @param agentId the agent ID
     * @return list of learning events
     */
    @GetMapping("/accessible-to/{agentId}")
    public ResponseEntity<List<LearningEvent>> getLearningEventsAccessibleToAgent(@PathVariable String agentId) {
        log.info("Received request to get learning events accessible to agent: {}", agentId);
        
        List<LearningEvent> events = learningService.getLearningEventsAccessibleToAgent(agentId);
        return ResponseEntity.ok(events);
    }

    /**
     * Get the content of a learning event as a specific type.
     *
     * @param eventId the event ID
     * @param contentType the class name of the content type
     * @return the content, or 404 if not found or cannot be converted
     */
    @GetMapping("/{eventId}/content")
    public ResponseEntity<Object> getLearningEventContent(
            @PathVariable String eventId,
            @RequestParam String contentType) {
        
        log.info("Received request to get content of learning event: {} as type: {}", eventId, contentType);
        
        try {
            Class<?> type = Class.forName(contentType);
            Optional<?> content = learningService.getLearningEventContent(eventId, type);
            return content.map(ResponseEntity::ok)
                    .orElse(ResponseEntity.notFound().build());
        } catch (ClassNotFoundException e) {
            log.error("Content type not found: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }

    /**
     * Add a related event to a learning event.
     *
     * @param eventId the event ID
     * @param request the related event request
     * @return the updated learning event, or 404 if not found
     */
    @PostMapping("/{eventId}/related-events")
    public ResponseEntity<LearningEvent> addRelatedEvent(
            @PathVariable String eventId,
            @RequestBody RelatedEventRequest request) {
        
        log.info("Received request to add related event {} to learning event: {}", 
                request.getRelatedEventId(), eventId);
        
        return learningService.addRelatedEvent(eventId, request.getRelatedEventId())
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Update a learning event's importance.
     *
     * @param eventId the event ID
     * @param request the importance update request
     * @return the updated learning event, or 404 if not found
     */
    @PutMapping("/{eventId}/importance")
    public ResponseEntity<LearningEvent> updateEventImportance(
            @PathVariable String eventId,
            @RequestBody ImportanceUpdateRequest request) {
        
        log.info("Received request to update importance for learning event: {} to {}", 
                eventId, request.getImportance());
        
        return learningService.updateEventImportance(eventId, request.getImportance())
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Find important learning events.
     *
     * @param minImportance the minimum importance
     * @return list of learning events
     */
    @GetMapping("/important")
    public ResponseEntity<List<LearningEvent>> findImportantLearningEvents(
            @RequestParam Float minImportance) {
        
        log.info("Received request to find important learning events with min importance: {}", minImportance);
        
        List<LearningEvent> events = learningService.findImportantLearningEvents(minImportance);
        return ResponseEntity.ok(events);
    }

    /**
     * Find recent learning events.
     *
     * @param since the time threshold
     * @return list of learning events
     */
    @GetMapping("/recent")
    public ResponseEntity<List<LearningEvent>> findRecentLearningEvents(
            @RequestParam LocalDateTime since) {
        
        log.info("Received request to find recent learning events since: {}", since);
        
        List<LearningEvent> events = learningService.findRecentLearningEvents(since);
        return ResponseEntity.ok(events);
    }

    /**
     * Apply learning from events to improve agent capabilities.
     *
     * @param request the learning application request
     * @return number of events processed
     */
    @PostMapping("/apply")
    public ResponseEntity<ApplyLearningResponse> applyLearning(@RequestBody ApplyLearningRequest request) {
        log.info("Received request to apply learning for agent: {} from event type: {}", 
                request.getAgentId(), request.getEventType());
        
        int count = learningService.applyLearning(request.getAgentId(), request.getEventType());
        ApplyLearningResponse response = new ApplyLearningResponse(count);
        return ResponseEntity.ok(response);
    }

    /**
     * Share learning between team members.
     *
     * @param request the learning sharing request
     * @return number of events shared
     */
    @PostMapping("/share")
    public ResponseEntity<ShareLearningResponse> shareLearning(@RequestBody ShareLearningRequest request) {
        log.info("Received request to share learning for team: {} from event type: {}", 
                request.getTeamId(), request.getEventType());
        
        int count = learningService.shareLearning(request.getTeamId(), request.getEventType());
        ShareLearningResponse response = new ShareLearningResponse(count);
        return ResponseEntity.ok(response);
    }

    /**
     * Learning event request.
     */
    public static class LearningEventRequest {
        private LearningEvent.LearningEventType eventType;
        private String agentId;
        private String taskId;
        private String teamId;
        private Object content;
        private Float importance;
        private Set<String> relatedEvents;

        // Getters and setters
        public LearningEvent.LearningEventType getEventType() { return eventType; }
        public void setEventType(LearningEvent.LearningEventType eventType) { this.eventType = eventType; }
        
        public String getAgentId() { return agentId; }
        public void setAgentId(String agentId) { this.agentId = agentId; }
        
        public String getTaskId() { return taskId; }
        public void setTaskId(String taskId) { this.taskId = taskId; }
        
        public String getTeamId() { return teamId; }
        public void setTeamId(String teamId) { this.teamId = teamId; }
        
        public Object getContent() { return content; }
        public void setContent(Object content) { this.content = content; }
        
        public Float getImportance() { return importance; }
        public void setImportance(Float importance) { this.importance = importance; }
        
        public Set<String> getRelatedEvents() { return relatedEvents; }
        public void setRelatedEvents(Set<String> relatedEvents) { this.relatedEvents = relatedEvents; }
    }

    /**
     * Related event request.
     */
    public static class RelatedEventRequest {
        private String relatedEventId;

        // Getters and setters
        public String getRelatedEventId() { return relatedEventId; }
        public void setRelatedEventId(String relatedEventId) { this.relatedEventId = relatedEventId; }
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
     * Apply learning request.
     */
    public static class ApplyLearningRequest {
        private String agentId;
        private LearningEvent.LearningEventType eventType;

        // Getters and setters
        public String getAgentId() { return agentId; }
        public void setAgentId(String agentId) { this.agentId = agentId; }
        
        public LearningEvent.LearningEventType getEventType() { return eventType; }
        public void setEventType(LearningEvent.LearningEventType eventType) { this.eventType = eventType; }
    }

    /**
     * Apply learning response.
     */
    public static class ApplyLearningResponse {
        private int processedCount;

        public ApplyLearningResponse(int processedCount) {
            this.processedCount = processedCount;
        }

        // Getters and setters
        public int getProcessedCount() { return processedCount; }
        public void setProcessedCount(int processedCount) { this.processedCount = processedCount; }
    }

    /**
     * Share learning request.
     */
    public static class ShareLearningRequest {
        private String teamId;
        private LearningEvent.LearningEventType eventType;

        // Getters and setters
        public String getTeamId() { return teamId; }
        public void setTeamId(String teamId) { this.teamId = teamId; }
        
        public LearningEvent.LearningEventType getEventType() { return eventType; }
        public void setEventType(LearningEvent.LearningEventType eventType) { this.eventType = eventType; }
    }

    /**
     * Share learning response.
     */
    public static class ShareLearningResponse {
        private int sharedCount;

        public ShareLearningResponse(int sharedCount) {
            this.sharedCount = sharedCount;
        }

        // Getters and setters
        public int getSharedCount() { return sharedCount; }
        public void setSharedCount(int sharedCount) { this.sharedCount = sharedCount; }
    }
}
