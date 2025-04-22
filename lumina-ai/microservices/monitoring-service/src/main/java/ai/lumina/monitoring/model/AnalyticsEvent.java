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
 * Represents an analytics event in the system.
 * Analytics events track user behavior, system usage, and business metrics.
 */
@Entity
@Table(name = "analytics_events")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AnalyticsEvent {

    @Id
    @Column(length = 36)
    private String id;

    /**
     * Type of event (e.g., "user_session", "feature_usage", "conversion")
     */
    @Column(nullable = false)
    private String eventType;

    /**
     * User identifier associated with the event (if applicable)
     */
    private String userId;

    /**
     * Service or component that generated the event
     */
    @Column(nullable = false)
    private String serviceName;

    /**
     * Timestamp when the event occurred
     */
    @Column(nullable = false)
    private Instant timestamp;

    /**
     * Properties/attributes of the event
     */
    @ElementCollection
    @CollectionTable(name = "analytics_event_properties", joinColumns = @JoinColumn(name = "event_id"))
    @MapKeyColumn(name = "property_key")
    @Column(name = "property_value", length = 1000)
    private Map<String, String> properties = new HashMap<>();
}
