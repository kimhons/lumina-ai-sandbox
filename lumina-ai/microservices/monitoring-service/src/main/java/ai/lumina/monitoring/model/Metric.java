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
 * Represents a metric data point in the monitoring system.
 * Metrics are used to track and analyze system performance and behavior.
 */
@Entity
@Table(name = "metrics")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Metric {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Name of the metric (e.g., "cpu_usage", "response_time", "error_rate")
     */
    @Column(nullable = false)
    private String name;

    /**
     * Value of the metric
     */
    @Column(nullable = false)
    private Double value;

    /**
     * Unit of measurement (e.g., "percent", "milliseconds", "count")
     */
    private String unit;

    /**
     * Timestamp when the metric was recorded
     */
    @Column(nullable = false)
    private Instant timestamp;

    /**
     * Service or component that generated the metric
     */
    @Column(nullable = false)
    private String source;

    /**
     * Additional labels/tags for the metric
     */
    @ElementCollection
    @CollectionTable(name = "metric_labels", joinColumns = @JoinColumn(name = "metric_id"))
    @MapKeyColumn(name = "label_key")
    @Column(name = "label_value")
    private Map<String, String> labels = new HashMap<>();
}
