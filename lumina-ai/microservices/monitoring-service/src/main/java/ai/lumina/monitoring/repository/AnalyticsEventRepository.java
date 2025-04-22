package ai.lumina.monitoring.repository;

import ai.lumina.monitoring.model.AnalyticsEvent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * Repository for managing AnalyticsEvent entities.
 */
@Repository
public interface AnalyticsEventRepository extends JpaRepository<AnalyticsEvent, String> {

    /**
     * Find analytics events by event type.
     *
     * @param eventType The type of the event
     * @return List of analytics events with the given type
     */
    List<AnalyticsEvent> findByEventType(String eventType);

    /**
     * Find analytics events by user ID.
     *
     * @param userId The ID of the user
     * @return List of analytics events for the given user
     */
    List<AnalyticsEvent> findByUserId(String userId);

    /**
     * Find analytics events by service name.
     *
     * @param serviceName The name of the service
     * @return List of analytics events from the given service
     */
    List<AnalyticsEvent> findByServiceName(String serviceName);

    /**
     * Find analytics events by event type and user ID.
     *
     * @param eventType The type of the event
     * @param userId The ID of the user
     * @return List of analytics events with the given type for the given user
     */
    List<AnalyticsEvent> findByEventTypeAndUserId(String eventType, String userId);

    /**
     * Find analytics events within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of analytics events within the time range
     */
    List<AnalyticsEvent> findByTimestampBetween(Instant startTime, Instant endTime);

    /**
     * Find analytics events by event type within a time range.
     *
     * @param eventType The type of the event
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of analytics events with the given type within the time range
     */
    List<AnalyticsEvent> findByEventTypeAndTimestampBetween(String eventType, Instant startTime, Instant endTime);

    /**
     * Find analytics events by user ID within a time range.
     *
     * @param userId The ID of the user
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of analytics events for the given user within the time range
     */
    List<AnalyticsEvent> findByUserIdAndTimestampBetween(String userId, Instant startTime, Instant endTime);

    /**
     * Count analytics events by event type within a time range.
     *
     * @param eventType The type of the event
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of analytics events with the given type within the time range
     */
    @Query("SELECT COUNT(e) FROM AnalyticsEvent e WHERE e.eventType = :eventType AND e.timestamp BETWEEN :startTime AND :endTime")
    Long countByEventTypeAndTimeRange(@Param("eventType") String eventType, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);

    /**
     * Count unique users by event type within a time range.
     *
     * @param eventType The type of the event
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of unique users for the given event type within the time range
     */
    @Query("SELECT COUNT(DISTINCT e.userId) FROM AnalyticsEvent e WHERE e.eventType = :eventType AND e.timestamp BETWEEN :startTime AND :endTime")
    Long countUniqueUsersByEventTypeAndTimeRange(@Param("eventType") String eventType, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);

    /**
     * Find the most recent analytics event for each user.
     *
     * @return List of the most recent analytics event for each user
     */
    @Query("SELECT e FROM AnalyticsEvent e WHERE e.timestamp = (SELECT MAX(e2.timestamp) FROM AnalyticsEvent e2 WHERE e2.userId = e.userId)")
    List<AnalyticsEvent> findMostRecentEventForEachUser();

    /**
     * Find analytics events with a specific property value.
     * Note: This is a native query that may be database-specific.
     *
     * @param propertyKey The key of the property
     * @param propertyValue The value of the property
     * @return List of analytics events with the given property value
     */
    @Query(value = "SELECT e.* FROM analytics_events e JOIN analytics_event_properties p ON e.id = p.event_id WHERE p.property_key = :propertyKey AND p.property_value = :propertyValue", nativeQuery = true)
    List<AnalyticsEvent> findByPropertyValue(@Param("propertyKey") String propertyKey, @Param("propertyValue") String propertyValue);
}
