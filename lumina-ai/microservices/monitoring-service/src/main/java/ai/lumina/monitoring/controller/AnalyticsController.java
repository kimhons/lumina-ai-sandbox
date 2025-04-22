package ai.lumina.monitoring.controller;

import ai.lumina.monitoring.model.AnalyticsEvent;
import ai.lumina.monitoring.service.AnalyticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * REST controller for managing analytics events in the monitoring system.
 */
@RestController
@RequestMapping("/api/analytics")
@RequiredArgsConstructor
public class AnalyticsController {

    private final AnalyticsService analyticsService;

    /**
     * Record an analytics event.
     *
     * @param request The analytics event request
     * @return The saved analytics event
     */
    @PostMapping("/events")
    public ResponseEntity<AnalyticsEvent> recordEvent(@RequestBody AnalyticsEventRequest request) {
        AnalyticsEvent event = analyticsService.recordEvent(
                request.getEventType(),
                request.getUserId(),
                request.getServiceName(),
                request.getProperties()
        );
        return ResponseEntity.ok(event);
    }

    /**
     * Get an analytics event by ID.
     *
     * @param eventId The ID of the event
     * @return The analytics event
     */
    @GetMapping("/events/{eventId}")
    public ResponseEntity<AnalyticsEvent> getEventById(@PathVariable String eventId) {
        return ResponseEntity.ok(analyticsService.getEventById(eventId));
    }

    /**
     * Get analytics events by event type.
     *
     * @param eventType The type of the event
     * @return List of analytics events with the given type
     */
    @GetMapping("/events/type/{eventType}")
    public ResponseEntity<List<AnalyticsEvent>> getEventsByType(@PathVariable String eventType) {
        return ResponseEntity.ok(analyticsService.getEventsByType(eventType));
    }

    /**
     * Get analytics events by user ID.
     *
     * @param userId The ID of the user
     * @return List of analytics events for the given user
     */
    @GetMapping("/events/user/{userId}")
    public ResponseEntity<List<AnalyticsEvent>> getEventsByUserId(@PathVariable String userId) {
        return ResponseEntity.ok(analyticsService.getEventsByUserId(userId));
    }

    /**
     * Get analytics events by service name.
     *
     * @param serviceName The name of the service
     * @return List of analytics events from the given service
     */
    @GetMapping("/events/service/{serviceName}")
    public ResponseEntity<List<AnalyticsEvent>> getEventsByServiceName(@PathVariable String serviceName) {
        return ResponseEntity.ok(analyticsService.getEventsByServiceName(serviceName));
    }

    /**
     * Get analytics events within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of analytics events within the time range
     */
    @GetMapping("/events/timerange")
    public ResponseEntity<List<AnalyticsEvent>> getEventsInTimeRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(analyticsService.getEventsInTimeRange(startTime, endTime));
    }

    /**
     * Get analytics events by event type within a time range.
     *
     * @param eventType The type of the event
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of analytics events with the given type within the time range
     */
    @GetMapping("/events/type/{eventType}/timerange")
    public ResponseEntity<List<AnalyticsEvent>> getEventsByTypeInTimeRange(
            @PathVariable String eventType,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(analyticsService.getEventsByTypeInTimeRange(eventType, startTime, endTime));
    }

    /**
     * Count analytics events by event type within a time range.
     *
     * @param eventType The type of the event
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of analytics events with the given type within the time range
     */
    @GetMapping("/events/type/{eventType}/count")
    public ResponseEntity<Long> countEventsByType(
            @PathVariable String eventType,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(analyticsService.countEventsByType(eventType, startTime, endTime));
    }

    /**
     * Count unique users by event type within a time range.
     *
     * @param eventType The type of the event
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of unique users for the given event type within the time range
     */
    @GetMapping("/events/type/{eventType}/unique-users")
    public ResponseEntity<Long> countUniqueUsersByEventType(
            @PathVariable String eventType,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(analyticsService.countUniqueUsersByEventType(eventType, startTime, endTime));
    }

    /**
     * Find the most recent analytics event for each user.
     *
     * @return List of the most recent analytics event for each user
     */
    @GetMapping("/events/users/most-recent")
    public ResponseEntity<List<AnalyticsEvent>> getMostRecentEventForEachUser() {
        return ResponseEntity.ok(analyticsService.getMostRecentEventForEachUser());
    }

    /**
     * Find analytics events with a specific property value.
     *
     * @param propertyKey The key of the property
     * @param propertyValue The value of the property
     * @return List of analytics events with the given property value
     */
    @GetMapping("/events/property")
    public ResponseEntity<List<AnalyticsEvent>> getEventsByPropertyValue(
            @RequestParam String propertyKey,
            @RequestParam String propertyValue) {
        return ResponseEntity.ok(analyticsService.getEventsByPropertyValue(propertyKey, propertyValue));
    }

    /**
     * Delete analytics events older than a specified time.
     *
     * @param cutoffTime The cutoff time
     * @return The number of analytics events deleted
     */
    @DeleteMapping("/events/cleanup")
    public ResponseEntity<Long> deleteEventsOlderThan(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant cutoffTime) {
        return ResponseEntity.ok(analyticsService.deleteEventsOlderThan(cutoffTime));
    }

    /**
     * Request object for recording an analytics event.
     */
    public static class AnalyticsEventRequest {
        private String eventType;
        private String userId;
        private String serviceName;
        private Map<String, String> properties;

        public String getEventType() {
            return eventType;
        }

        public void setEventType(String eventType) {
            this.eventType = eventType;
        }

        public String getUserId() {
            return userId;
        }

        public void setUserId(String userId) {
            this.userId = userId;
        }

        public String getServiceName() {
            return serviceName;
        }

        public void setServiceName(String serviceName) {
            this.serviceName = serviceName;
        }

        public Map<String, String> getProperties() {
            return properties;
        }

        public void setProperties(Map<String, String> properties) {
            this.properties = properties;
        }
    }
}
