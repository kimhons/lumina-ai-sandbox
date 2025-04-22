package ai.lumina.security.repository;

import ai.lumina.security.model.AuditLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Repository interface for managing AuditLog entities.
 */
@Repository
public interface AuditLogRepository extends JpaRepository<AuditLog, Long> {

    /**
     * Find audit logs by event type.
     *
     * @param eventType The event type
     * @return List of matching audit logs
     */
    List<AuditLog> findByEventType(AuditLog.EventType eventType);

    /**
     * Find audit logs by event source.
     *
     * @param eventSource The event source
     * @return List of matching audit logs
     */
    List<AuditLog> findByEventSource(String eventSource);

    /**
     * Find audit logs by user ID.
     *
     * @param userId The user ID
     * @return List of matching audit logs
     */
    List<AuditLog> findByUserId(String userId);

    /**
     * Find audit logs by username.
     *
     * @param username The username
     * @return List of matching audit logs
     */
    List<AuditLog> findByUsername(String username);

    /**
     * Find audit logs by resource ID.
     *
     * @param resourceId The resource ID
     * @return List of matching audit logs
     */
    List<AuditLog> findByResourceId(String resourceId);

    /**
     * Find audit logs by resource type.
     *
     * @param resourceType The resource type
     * @return List of matching audit logs
     */
    List<AuditLog> findByResourceType(String resourceType);

    /**
     * Find audit logs by action.
     *
     * @param action The action
     * @return List of matching audit logs
     */
    List<AuditLog> findByAction(String action);

    /**
     * Find audit logs by status.
     *
     * @param status The status
     * @return List of matching audit logs
     */
    List<AuditLog> findByStatus(AuditLog.EventStatus status);

    /**
     * Find audit logs by severity.
     *
     * @param severity The severity
     * @return List of matching audit logs
     */
    List<AuditLog> findBySeverity(AuditLog.EventSeverity severity);

    /**
     * Find audit logs by IP address.
     *
     * @param ipAddress The IP address
     * @return List of matching audit logs
     */
    List<AuditLog> findByIpAddress(String ipAddress);

    /**
     * Find audit logs within a time range.
     *
     * @param startTime The start time
     * @param endTime The end time
     * @return List of matching audit logs
     */
    List<AuditLog> findByTimestampBetween(LocalDateTime startTime, LocalDateTime endTime);

    /**
     * Find audit logs by multiple criteria.
     *
     * @param eventType The event type
     * @param status The status
     * @param severity The severity
     * @return List of matching audit logs
     */
    List<AuditLog> findByEventTypeAndStatusAndSeverity(
            AuditLog.EventType eventType,
            AuditLog.EventStatus status,
            AuditLog.EventSeverity severity);

    /**
     * Find the most recent audit logs.
     *
     * @param limit The maximum number of logs to return
     * @return List of recent audit logs
     */
    @Query(value = "SELECT a FROM AuditLog a ORDER BY a.timestamp DESC")
    List<AuditLog> findMostRecent(int limit);
}
