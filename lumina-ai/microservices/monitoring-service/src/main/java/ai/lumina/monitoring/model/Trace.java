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
 * Represents a trace in a distributed tracing system.
 * Traces track the flow of requests across multiple services and components.
 */
@Entity
@Table(name = "traces")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Trace {

    @Id
    @Column(length = 36)
    private String id;

    /**
     * Name of the trace (typically the operation being traced)
     */
    @Column(nullable = false)
    private String name;

    /**
     * Service that initiated the trace
     */
    @Column(nullable = false)
    private String serviceName;

    /**
     * Timestamp when the trace was started
     */
    @Column(nullable = false)
    private Instant startTime;

    /**
     * Timestamp when the trace was completed
     */
    private Instant endTime;

    /**
     * Duration of the trace in milliseconds
     */
    private Long durationMs;

    /**
     * Status of the trace (e.g., "success", "error")
     */
    private String status;

    /**
     * Additional attributes for the trace
     */
    @ElementCollection
    @CollectionTable(name = "trace_attributes", joinColumns = @JoinColumn(name = "trace_id"))
    @MapKeyColumn(name = "attribute_key")
    @Column(name = "attribute_value")
    private Map<String, String> attributes = new HashMap<>();
}
