package ai.lumina.collaboration.service;

import ai.lumina.collaboration.model.LearningEvent;
import ai.lumina.collaboration.repository.LearningEventRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

/**
 * Service for managing collaborative learning events in the collaboration system.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class CollaborativeLearningService {

    private final LearningEventRepository learningEventRepository;
    private final ObjectMapper objectMapper;

    /**
     * Record a new learning event.
     *
     * @param eventType the learning event type
     * @param agentId the agent ID
     * @param taskId optional task ID
     * @param teamId optional team ID
     * @param content the event content
     * @param importance the importance (0.0 to 1.0)
     * @param relatedEvents optional set of related event IDs
     * @return the created learning event
     * @throws JsonProcessingException if content cannot be serialized to JSON
     */
    @Transactional
    public LearningEvent recordLearningEvent(
            LearningEvent.LearningEventType eventType,
            String agentId,
            String taskId,
            String teamId,
            Object content,
            Float importance,
            Set<String> relatedEvents) throws JsonProcessingException {
        
        log.info("Recording learning event of type {} by {}", eventType, agentId);
        
        // Convert content to JSON
        String contentJson = objectMapper.writeValueAsString(content);
        
        // Create learning event
        String eventId = UUID.randomUUID().toString();
        LocalDateTime now = LocalDateTime.now();
        
        LearningEvent learningEvent = LearningEvent.builder()
                .eventId(eventId)
                .eventType(eventType)
                .agentId(agentId)
                .taskId(taskId)
                .teamId(teamId)
                .contentJson(contentJson)
                .importance(importance)
                .relatedEvents(relatedEvents != null ? relatedEvents : new HashSet<>())
                .createdAt(now)
                .build();
        
        return learningEventRepository.save(learningEvent);
    }

    /**
     * Get a learning event by ID.
     *
     * @param eventId the event ID
     * @return the learning event, or empty if not found
     */
    @Transactional(readOnly = true)
    public Optional<LearningEvent> getLearningEvent(String eventId) {
        return learningEventRepository.findByEventId(eventId);
    }

    /**
     * Get learning events by type.
     *
     * @param eventType the event type
     * @return list of learning events
     */
    @Transactional(readOnly = true)
    public List<LearningEvent> getLearningEventsByType(LearningEvent.LearningEventType eventType) {
        return learningEventRepository.findByEventType(eventType);
    }

    /**
     * Get learning events by agent ID.
     *
     * @param agentId the agent ID
     * @return list of learning events
     */
    @Transactional(readOnly = true)
    public List<LearningEvent> getLearningEventsByAgent(String agentId) {
        return learningEventRepository.findByAgentId(agentId);
    }

    /**
     * Get learning events by task ID.
     *
     * @param taskId the task ID
     * @return list of learning events
     */
    @Transactional(readOnly = true)
    public List<LearningEvent> getLearningEventsByTask(String taskId) {
        return learningEventRepository.findByTaskId(taskId);
    }

    /**
     * Get learning events by team ID.
     *
     * @param teamId the team ID
     * @return list of learning events
     */
    @Transactional(readOnly = true)
    public List<LearningEvent> getLearningEventsByTeam(String teamId) {
        return learningEventRepository.findByTeamId(teamId);
    }

    /**
     * Get learning events by agent ID and event type.
     *
     * @param agentId the agent ID
     * @param eventType the event type
     * @return list of learning events
     */
    @Transactional(readOnly = true)
    public List<LearningEvent> getLearningEventsByAgentAndType(String agentId, LearningEvent.LearningEventType eventType) {
        return learningEventRepository.findByAgentIdAndEventType(agentId, eventType);
    }

    /**
     * Get learning events by team ID and event type.
     *
     * @param teamId the team ID
     * @param eventType the event type
     * @return list of learning events
     */
    @Transactional(readOnly = true)
    public List<LearningEvent> getLearningEventsByTeamAndType(String teamId, LearningEvent.LearningEventType eventType) {
        return learningEventRepository.findByTeamIdAndEventType(teamId, eventType);
    }

    /**
     * Get learning events related to a specific event.
     *
     * @param eventId the related event ID
     * @return list of learning events
     */
    @Transactional(readOnly = true)
    public List<LearningEvent> getRelatedLearningEvents(String eventId) {
        return learningEventRepository.findByRelatedEvent(eventId);
    }

    /**
     * Get learning events accessible to an agent.
     *
     * @param agentId the agent ID
     * @return list of learning events
     */
    @Transactional(readOnly = true)
    public List<LearningEvent> getLearningEventsAccessibleToAgent(String agentId) {
        return learningEventRepository.findAccessibleToAgent(agentId);
    }

    /**
     * Get the content of a learning event as a specific type.
     *
     * @param eventId the event ID
     * @param contentType the class of the content type
     * @param <T> the content type
     * @return the content, or empty if not found or cannot be converted
     */
    @Transactional(readOnly = true)
    public <T> Optional<T> getLearningEventContent(String eventId, Class<T> contentType) {
        Optional<LearningEvent> eventOpt = learningEventRepository.findByEventId(eventId);
        if (eventOpt.isPresent()) {
            LearningEvent event = eventOpt.get();
            try {
                T content = objectMapper.readValue(event.getContentJson(), contentType);
                return Optional.of(content);
            } catch (JsonProcessingException e) {
                log.error("Failed to deserialize learning event content: {}", e.getMessage());
                return Optional.empty();
            }
        }
        return Optional.empty();
    }

    /**
     * Add a related event to a learning event.
     *
     * @param eventId the event ID
     * @param relatedEventId the related event ID to add
     * @return the updated learning event, or empty if not found
     */
    @Transactional
    public Optional<LearningEvent> addRelatedEvent(String eventId, String relatedEventId) {
        Optional<LearningEvent> eventOpt = learningEventRepository.findByEventId(eventId);
        Optional<LearningEvent> relatedEventOpt = learningEventRepository.findByEventId(relatedEventId);
        
        if (eventOpt.isPresent() && relatedEventOpt.isPresent()) {
            LearningEvent event = eventOpt.get();
            Set<String> relatedEvents = new HashSet<>(event.getRelatedEvents());
            relatedEvents.add(relatedEventId);
            event.setRelatedEvents(relatedEvents);
            return Optional.of(learningEventRepository.save(event));
        }
        return Optional.empty();
    }

    /**
     * Update a learning event's importance.
     *
     * @param eventId the event ID
     * @param importance the new importance
     * @return the updated learning event, or empty if not found
     */
    @Transactional
    public Optional<LearningEvent> updateEventImportance(String eventId, Float importance) {
        Optional<LearningEvent> eventOpt = learningEventRepository.findByEventId(eventId);
        if (eventOpt.isPresent()) {
            LearningEvent event = eventOpt.get();
            event.setImportance(importance);
            return Optional.of(learningEventRepository.save(event));
        }
        return Optional.empty();
    }

    /**
     * Find important learning events.
     *
     * @param minImportance the minimum importance
     * @return list of learning events
     */
    @Transactional(readOnly = true)
    public List<LearningEvent> findImportantLearningEvents(Float minImportance) {
        return learningEventRepository.findByImportanceGreaterThanEqual(minImportance);
    }

    /**
     * Find recent learning events.
     *
     * @param since the time threshold
     * @return list of learning events
     */
    @Transactional(readOnly = true)
    public List<LearningEvent> findRecentLearningEvents(LocalDateTime since) {
        return learningEventRepository.findByCreatedAtGreaterThan(since);
    }

    /**
     * Apply learning from events to improve agent capabilities.
     * This is a simplified implementation that would be expanded in a real system.
     *
     * @param agentId the agent ID
     * @param eventType the event type to learn from
     * @return number of events processed
     */
    @Transactional
    public int applyLearning(String agentId, LearningEvent.LearningEventType eventType) {
        List<LearningEvent> events = learningEventRepository.findByAgentIdAndEventType(agentId, eventType);
        
        // In a real implementation, this would analyze events and update agent capabilities
        log.info("Applied learning from {} events of type {} for agent {}", events.size(), eventType, agentId);
        
        return events.size();
    }

    /**
     * Share learning between team members.
     * This is a simplified implementation that would be expanded in a real system.
     *
     * @param teamId the team ID
     * @param eventType the event type to share
     * @return number of events shared
     */
    @Transactional
    public int shareLearning(String teamId, LearningEvent.LearningEventType eventType) {
        List<LearningEvent> events = learningEventRepository.findByTeamIdAndEventType(teamId, eventType);
        
        // In a real implementation, this would share learning events between team members
        log.info("Shared {} learning events of type {} within team {}", events.size(), eventType, teamId);
        
        return events.size();
    }
}
