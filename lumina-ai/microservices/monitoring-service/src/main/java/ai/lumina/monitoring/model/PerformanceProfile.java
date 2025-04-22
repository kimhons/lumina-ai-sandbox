package ai.lumina.monitoring.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.persistence.*;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

/**
 * Represents a performance profile for a service or operation.
 * Performance profiles track execution times and resource usage for optimization.
 */
@Entity
@Table(name = "performance_profiles")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PerformanceProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Name of the operation being profiled
     */
    @Column(nullable = false)
    private String operationName;

    /**
     * Service or component that was profiled
     */
    @Column(nullable = false)
    private String serviceName;

    /**
     * Timestamp when the profile was recorded
     */
    @Column(nullable = false)
    private Instant timestamp;

    /**
     * Duration of the operation in milliseconds
     */
    @Column(nullable = false)
    private Double durationMs;

    /**
     * CPU usage percentage during the operation
     */
    private Double cpuPercent;

    /**
     * Memory usage in bytes during the operation
     */
    private Long memoryBytes;

    /**
     * Memory change in bytes during the operation
     */
    private Long memoryDeltaBytes;

    /**
     * Whether an error occurred during the operation
     */
    private Boolean error;

    /**
     * Additional attributes for the profile
     */
    @ElementCollection
    @CollectionTable(name = "profile_attributes", joinColumns = @JoinColumn(name = "profile_id"))
    @MapKeyColumn(name = "attribute_key")
    @Column(name = "attribute_value")
    private Map<String, String> attributes = new HashMap<>();
}
