package ai.lumina.monitoring.service;

import ai.lumina.monitoring.model.AnalyticsEvent;
import ai.lumina.monitoring.repository.AnalyticsEventRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Service for managing analytics events in the monitoring system.
 * This service provides functionality for collecting, storing, and analyzing user and system events.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AnalyticsService {

    private final AnalyticsEventRepository analyticsEventRepository;

    /**
     * Record an analytics event.
     *
     * @param eventType The type of the event
     * @param userId The ID of the user (optional)
     * @param serviceName The name of the service
     * @param properties Additional properties for the event
     * @return The saved analytics event
     */
    @Transactional
    public AnalyticsEvent recordEvent(String eventType, String userId, String serviceName, Map<String, String> properties) {
        String eventId = UUID.randomUUID().toString();
        AnalyticsEvent event = AnalyticsEvent.builder()
                .id(eventId)
                .eventType(eventType)
                .userId(userId)
                .serviceName(serviceName)
                .timestamp(Instant.now())
                .properties(properties != null ? properties : new HashMap<>())
                .build();
        
        log.debug("Recording analytics event: {}", event);
        return analyticsEventRepository.save(event);
    }

    /**
     * Get an analytics event by ID.
     *
     * @param eventId The ID of the event
     * @return The analytics event
     */
    @Transactional(readOnly = true)
    public AnalyticsEvent getEventById(String eventId) {
        return analyticsEventRepository.findById(eventId)
                .orElseThrow(() -> new IllegalArgumentException("Analytics event not found: " + eventId));
    }

    /**
     * Get analytics events by event type.
     *
     * @param eventType The type of the event
     * @return List of analytics events with the given type
     */
    @Transactional(readOnly = true)
    public List<AnalyticsEvent> getEventsByType(String eventType) {
        return analyticsEventRepository.findByEventType(eventType);
    }

    /**
     * Get analytics events by user ID.
     *
     * @param userId The ID of the user
     * @return List of analytics events for the given user
     */
    @Transactional(readOnly = true)
    public List<AnalyticsEvent> getEventsByUserId(String userId) {
        return analyticsEventRepository.findByUserId(userId);
    }

    /**
     * Get analytics events by service name.
     *
     * @param serviceName The name of the service
     * @return List of analytics events from the given service
     */
    @Transactional(readOnly = true)
    public List<AnalyticsEvent> getEventsByServiceName(String serviceName) {
        return analyticsEventRepository.findByServiceName(serviceName);
    }

    /**
     * Get analytics events within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of analytics events within the time range
     */
    @Transactional(readOnly = true)
    public List<AnalyticsEvent> getEventsInTimeRange(Instant startTime, Instant endTime) {
        return analyticsEventRepository.findByTimestampBetween(startTime, endTime);
    }

    /**
     * Get analytics events by event type within a time range.
     *
     * @param eventType The type of the event
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of analytics events with the given type within the time range
     */
    @Transactional(readOnly = true)
    public List<AnalyticsEvent> getEventsByTypeInTimeRange(String eventType, Instant startTime, Instant endTime) {
        return analyticsEventRepository.findByEventTypeAndTimestampBetween(eventType, startTime, endTime);
    }

    /**
     * Count analytics events by event type within a time range.
     *
     * @param eventType The type of the event
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of analytics events with the given type within the time range
     */
    @Transactional(readOnly = true)
    public Long countEventsByType(String eventType, Instant startTime, Instant endTime) {
        return analyticsEventRepository.countByEventTypeAndTimeRange(eventType, startTime, endTime);
    }

    /**
     * Count unique users by event type within a time range.
     *
     * @param eventType The type of the event
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of unique users for the given event type within the time range
     */
    @Transactional(readOnly = true)
    public Long countUniqueUsersByEventType(String eventType, Instant startTime, Instant endTime) {
        return analyticsEventRepository.countUniqueUsersByEventTypeAndTimeRange(eventType, startTime, endTime);
    }

    /**
     * Find the most recent analytics event for each user.
     *
     * @return List of the most recent analytics event for each user
     */
    @Transactional(readOnly = true)
    public List<AnalyticsEvent> getMostRecentEventForEachUser() {
        return analyticsEventRepository.findMostRecentEventForEachUser();
    }

    /**
     * Find analytics events with a specific property value.
     *
     * @param propertyKey The key of the property
     * @param propertyValue The value of the property
     * @return List of analytics events with the given property value
     */
    @Transactional(readOnly = true)
    public List<AnalyticsEvent> getEventsByPropertyValue(String propertyKey, String propertyValue) {
        return analyticsEventRepository.findByPropertyValue(propertyKey, propertyValue);
    }

    /**
     * Delete analytics events older than a specified time.
     *
     * @param cutoffTime The cutoff time
     * @return The number of analytics events deleted
     */
    @Transactional
    public long deleteEventsOlderThan(Instant cutoffTime) {
        List<AnalyticsEvent> oldEvents = analyticsEventRepository.findAll().stream()
                .filter(event -> event.getTimestamp().isBefore(cutoffTime))
                .toList();
        
        if (!oldEvents.isEmpty()) {
            analyticsEventRepository.deleteAll(oldEvents);
            log.info("Deleted {} analytics events older than {}", oldEvents.size(), cutoffTime);
        }
        
        return oldEvents.size();
    }
}
