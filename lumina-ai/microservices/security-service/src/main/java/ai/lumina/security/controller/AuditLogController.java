package ai.lumina.security.controller;

import ai.lumina.security.model.AuditLog;
import ai.lumina.security.service.AuditLogService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

/**
 * REST controller for audit logging operations.
 */
@RestController
@RequestMapping("/api/security/audit")
@RequiredArgsConstructor
@Slf4j
public class AuditLogController {

    private final AuditLogService auditLogService;

    /**
     * Create a new audit log entry.
     *
     * @param auditLog The audit log to create
     * @return The created audit log
     */
    @PostMapping("/logs")
    public ResponseEntity<AuditLog> createAuditLog(@RequestBody AuditLog auditLog) {
        log.info("REST request to create audit log entry");
        AuditLog createdLog = auditLogService.createAuditLog(auditLog);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdLog);
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
    @PostMapping("/logs/authentication")
    public ResponseEntity<AuditLog> logAuthenticationEvent(
            @RequestParam String userId,
            @RequestParam String username,
            @RequestParam AuditLog.EventStatus status,
            @RequestParam String description,
            @RequestParam(required = false) String ipAddress,
            @RequestParam(required = false) String userAgent) {
        log.info("REST request to log authentication event for user: {}", username);
        AuditLog auditLog = auditLogService.logAuthenticationEvent(
                userId, username, status, description, ipAddress, userAgent);
        return ResponseEntity.status(HttpStatus.CREATED).body(auditLog);
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
    @PostMapping("/logs/authorization")
    public ResponseEntity<AuditLog> logAuthorizationEvent(
            @RequestParam String userId,
            @RequestParam String username,
            @RequestParam String resourceId,
            @RequestParam String resourceType,
            @RequestParam String action,
            @RequestParam AuditLog.EventStatus status,
            @RequestParam String description) {
        log.info("REST request to log authorization event for user: {}", username);
        AuditLog auditLog = auditLogService.logAuthorizationEvent(
                userId, username, resourceId, resourceType, action, status, description);
        return ResponseEntity.status(HttpStatus.CREATED).body(auditLog);
    }

    /**
     * Get an audit log by ID.
     *
     * @param id The audit log ID
     * @return The audit log if found
     */
    @GetMapping("/logs/{id}")
    public ResponseEntity<AuditLog> getAuditLog(@PathVariable Long id) {
        log.info("REST request to get audit log with ID: {}", id);
        return auditLogService.getAuditLogById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get all audit logs.
     *
     * @return List of all audit logs
     */
    @GetMapping("/logs")
    public ResponseEntity<List<AuditLog>> getAllAuditLogs() {
        log.info("REST request to get all audit logs");
        List<AuditLog> logs = auditLogService.getAllAuditLogs();
        return ResponseEntity.ok(logs);
    }

    /**
     * Get audit logs by event type.
     *
     * @param eventType The event type
     * @return List of matching audit logs
     */
    @GetMapping("/logs/by-event-type/{eventType}")
    public ResponseEntity<List<AuditLog>> getAuditLogsByEventType(
            @PathVariable AuditLog.EventType eventType) {
        log.info("REST request to get audit logs by event type: {}", eventType);
        List<AuditLog> logs = auditLogService.getAuditLogsByEventType(eventType);
        return ResponseEntity.ok(logs);
    }

    /**
     * Get audit logs by user ID.
     *
     * @param userId The user ID
     * @return List of matching audit logs
     */
    @GetMapping("/logs/by-user/{userId}")
    public ResponseEntity<List<AuditLog>> getAuditLogsByUserId(@PathVariable String userId) {
        log.info("REST request to get audit logs by user ID: {}", userId);
        List<AuditLog> logs = auditLogService.getAuditLogsByUserId(userId);
        return ResponseEntity.ok(logs);
    }

    /**
     * Get audit logs by time range.
     *
     * @param startTime The start time
     * @param endTime The end time
     * @return List of matching audit logs
     */
    @GetMapping("/logs/by-time-range")
    public ResponseEntity<List<AuditLog>> getAuditLogsByTimeRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime endTime) {
        log.info("REST request to get audit logs between {} and {}", startTime, endTime);
        List<AuditLog> logs = auditLogService.getAuditLogsByTimeRange(startTime, endTime);
        return ResponseEntity.ok(logs);
    }

    /**
     * Get the most recent audit logs.
     *
     * @param limit The maximum number of logs to return
     * @return List of recent audit logs
     */
    @GetMapping("/logs/recent")
    public ResponseEntity<List<AuditLog>> getMostRecentAuditLogs(
            @RequestParam(defaultValue = "100") int limit) {
        log.info("REST request to get the most recent {} audit logs", limit);
        List<AuditLog> logs = auditLogService.getMostRecentAuditLogs(limit);
        return ResponseEntity.ok(logs);
    }
}
