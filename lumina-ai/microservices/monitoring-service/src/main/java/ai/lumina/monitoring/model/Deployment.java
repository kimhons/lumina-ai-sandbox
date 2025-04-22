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
 * Represents a deployment record in the system.
 * Deployment records track the deployment of services and applications.
 */
@Entity
@Table(name = "deployments")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Deployment {

    @Id
    @Column(length = 36)
    private String id;

    /**
     * Name of the service being deployed
     */
    @Column(nullable = false)
    private String serviceName;

    /**
     * Version being deployed
     */
    @Column(nullable = false)
    private String version;

    /**
     * Environment where the deployment is taking place (e.g., "development", "staging", "production")
     */
    @Column(nullable = false)
    private String environment;

    /**
     * Timestamp when the deployment was initiated
     */
    @Column(nullable = false)
    private Instant timestamp;

    /**
     * Timestamp when the deployment started
     */
    private Instant startTime;

    /**
     * Timestamp when the deployment ended
     */
    private Instant endTime;

    /**
     * Status of the deployment (e.g., "prepared", "in_progress", "completed", "failed")
     */
    @Column(nullable = false)
    private String status;

    /**
     * Path to the deployment artifact
     */
    private String artifactPath;

    /**
     * Checksum of the deployment artifact
     */
    private String artifactChecksum;

    /**
     * Error message if the deployment failed
     */
    @Column(length = 2000)
    private String error;

    /**
     * Deployment strategy used (e.g., "rolling", "blue_green", "canary")
     */
    private String deploymentStrategy;

    /**
     * Additional properties for the deployment
     */
    @ElementCollection
    @CollectionTable(name = "deployment_properties", joinColumns = @JoinColumn(name = "deployment_id"))
    @MapKeyColumn(name = "property_key")
    @Column(name = "property_value", length = 1000)
    private Map<String, String> properties = new HashMap<>();
}
