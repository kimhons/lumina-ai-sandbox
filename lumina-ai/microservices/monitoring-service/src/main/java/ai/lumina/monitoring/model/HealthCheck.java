package ai.lumina.monitoring.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

/**
 * Represents a health check result for a service or component.
 * Health checks are used to monitor the operational status of system components.
 */
@Entity
@Table(name = "health_checks")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class HealthCheck {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Name of the component being checked
     */
    @Column(nullable = false)
    private String componentName;

    /**
     * Type of component (e.g., "service", "database", "cache", "api")
     */
    @Column(nullable = false)
    private String componentType;

    /**
     * Status of the health check (e.g., "healthy", "degraded", "unhealthy")
     */
    @Column(nullable = false)
    private String status;

    /**
     * Timestamp when the health check was performed
     */
    @Column(nullable = false)
    private Instant timestamp;

    /**
     * Response time of the health check in milliseconds
     */
    private Long responseTimeMs;

    /**
     * Detailed message about the health check result
     */
    @Column(length = 1000)
    private String message;

    /**
     * List of sub-checks that make up this health check
     */
    @ElementCollection
    @CollectionTable(name = "health_check_details", joinColumns = @JoinColumn(name = "health_check_id"))
    private List<HealthCheckDetail> details = new ArrayList<>();

    /**
     * Represents a detailed sub-check within a health check
     */
    @Embeddable
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class HealthCheckDetail {
        
        /**
         * Name of the sub-check
         */
        private String name;
        
        /**
         * Status of the sub-check
         */
        private String status;
        
        /**
         * Message for the sub-check
         */
        private String message;
    }
}
