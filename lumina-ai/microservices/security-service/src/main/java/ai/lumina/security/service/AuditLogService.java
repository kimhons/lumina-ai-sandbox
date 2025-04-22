package ai.lumina.security.service;

import ai.lumina.security.model.AuditLog;
import ai.lumina.security.repository.AuditLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Service for managing audit logs.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AuditLogService {

    private final AuditLogRepository auditLogRepository;

    /**
     * Create a new audit log entry.
     *
     * @param auditLog The audit log to create
     * @return The created audit log
     */
    @Transactional
    public AuditLog createAuditLog(AuditLog auditLog) {
        log.debug("Creating audit log entry: {}", auditLog.getEventDescription());
        return auditLogRepository.save(auditLog);
    }

    /**
     * Log an authentication event.
     *
     * @param userId The user ID
     * @param username The username
     * @param status The event status
     * @param description The event description
     * @param ipAddress The IP address
     * @param userAgent The user agent
     * @return The created audit log
     */
    @Transactional
    public AuditLog logAuthenticationEvent(
            String userId,
            String username,
            AuditLog.EventStatus status,
            String description,
            String ipAddress,
            String userAgent) {
        
        AuditLog auditLog = AuditLog.builder()
                .eventType(AuditLog.EventType.AUTHENTICATION)
                .eventSource("AuthenticationService")
                .eventDescription(description)
                .userId(userId)
                .username(username)
                .status(status)
                .severity(determineSeverity(status))
                .ipAddress(ipAddress)
                .userAgent(userAgent)
                .build();
        
        return createAuditLog(auditLog);
    }

    /**
     * Log an authorization event.
     *
     * @param userId The user ID
     * @param username The username
     * @param resourceId The resource ID
     * @param resourceType The resource type
     * @param action The action
     * @param status The event status
     * @param description The event description
     * @return The created audit log
     */
    @Transactional
    public AuditLog logAuthorizationEvent(
            String userId,
            String username,
            String resourceId,
            String resourceType,
            String action,
            AuditLog.EventStatus status,
            String description) {
        
        AuditLog auditLog = AuditLog.builder()
                .eventType(AuditLog.EventType.AUTHORIZATION)
                .eventSource("AccessControlService")
                .eventDescription(description)
                .userId(userId)
                .username(username)
                .resourceId(resourceId)
                .resourceType(resourceType)
                .action(action)
                .status(status)
                .severity(determineSeverity(status))
                .build();
        
        return createAuditLog(auditLog);
    }

    /**
     * Log a data access event.
     *
     * @param userId The user ID
     * @param username The username
     * @param resourceId The resource ID
     * @param resourceType The resource type
     * @param action The action
     * @param status The event status
     * @param description The event description
     * @return The created audit log
     */
    @Transactional
    public AuditLog logDataAccessEvent(
            String userId,
            String username,
            String resourceId,
            String resourceType,
            String action,
            AuditLog.EventStatus status,
            String description) {
        
        AuditLog auditLog = AuditLog.builder()
                .eventType(AuditLog.EventType.DATA_ACCESS)
                .eventSource("DataAccessService")
                .eventDescription(description)
                .userId(userId)
                .username(username)
                .resourceId(resourceId)
                .resourceType(resourceType)
                .action(action)
                .status(status)
                .severity(determineSeverity(status))
                .build();
        
        return createAuditLog(auditLog);
    }

    /**
     * Get an audit log by ID.
     *
     * @param id The audit log ID
     * @return The audit log if found
     */
    @Transactional(readOnly = true)
    public Optional<AuditLog> getAuditLogById(Long id) {
        return auditLogRepository.findById(id);
    }

    /**
     * Get all audit logs.
     *
     * @return List of all audit logs
     */
    @Transactional(readOnly = true)
    public List<AuditLog> getAllAuditLogs() {
        return auditLogRepository.findAll();
    }

    /**
     * Get audit logs by event type.
     *
     * @param eventType The event type
     * @return List of matching audit logs
     */
    @Transactional(readOnly = true)
    public List<AuditLog> getAuditLogsByEventType(AuditLog.EventType eventType) {
        return auditLogRepository.findByEventType(eventType);
    }

    /**
     * Get audit logs by user ID.
     *
     * @param userId The user ID
     * @return List of matching audit logs
     */
    @Transactional(readOnly = true)
    public List<AuditLog> getAuditLogsByUserId(String userId) {
        return auditLogRepository.findByUserId(userId);
    }

    /**
     * Get audit logs by time range.
     *
     * @param startTime The start time
     * @param endTime The end time
     * @return List of matching audit logs
     */
    @Transactional(readOnly = true)
    public List<AuditLog> getAuditLogsByTimeRange(LocalDateTime startTime, LocalDateTime endTime) {
        return auditLogRepository.findByTimestampBetween(startTime, endTime);
    }

    /**
     * Get the most recent audit logs.
     *
     * @param limit The maximum number of logs to return
     * @return List of recent audit logs
     */
    @Transactional(readOnly = true)
    public List<AuditLog> getMostRecentAuditLogs(int limit) {
        return auditLogRepository.findMostRecent(limit);
    }

    /**
     * Determine the severity based on the event status.
     *
     * @param status The event status
     * @return The appropriate severity
     */
    private AuditLog.EventSeverity determineSeverity(AuditLog.EventStatus status) {
        switch (status) {
            case SUCCESS:
                return AuditLog.EventSeverity.INFO;
            case FAILURE:
                return AuditLog.EventSeverity.HIGH;
            case WARNING:
                return AuditLog.EventSeverity.MEDIUM;
            case INFO:
                return AuditLog.EventSeverity.LOW;
            default:
                return AuditLog.EventSeverity.INFO;
        }
    }
}
