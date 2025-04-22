package ai.lumina.security.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Represents an audit log entry in the system.
 * Records security-related events for compliance and monitoring purposes.
 */
@Entity
@Table(name = "audit_logs")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AuditLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private EventType eventType;

    @Column(nullable = false)
    private String eventSource;

    @Column(nullable = false)
    private String eventDescription;

    @Column(nullable = false)
    private String userId;

    @Column(nullable = true)
    private String username;

    @Column(nullable = true)
    private String resourceId;

    @Column(nullable = true)
    private String resourceType;

    @Column(nullable = true)
    private String action;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private EventStatus status;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private EventSeverity severity;

    @Column(nullable = true, length = 4000)
    private String metadata;

    @Column(nullable = true)
    private String ipAddress;

    @Column(nullable = true)
    private String userAgent;

    @Column(nullable = false)
    private LocalDateTime timestamp;

    /**
     * Enum representing the type of audit event.
     */
    public enum EventType {
        AUTHENTICATION,
        AUTHORIZATION,
        DATA_ACCESS,
        CONFIGURATION_CHANGE,
        USER_MANAGEMENT,
        SYSTEM_OPERATION,
        SECURITY_ALERT,
        COMPLIANCE_CHECK
    }

    /**
     * Enum representing the status of the audit event.
     */
    public enum EventStatus {
        SUCCESS,
        FAILURE,
        WARNING,
        INFO
    }

    /**
     * Enum representing the severity of the audit event.
     */
    public enum EventSeverity {
        CRITICAL,
        HIGH,
        MEDIUM,
        LOW,
        INFO
    }

    @PrePersist
    protected void onCreate() {
        timestamp = LocalDateTime.now();
    }
}
