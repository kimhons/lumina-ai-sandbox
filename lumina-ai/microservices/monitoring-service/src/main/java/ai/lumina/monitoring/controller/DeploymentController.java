package ai.lumina.monitoring.controller;

import ai.lumina.monitoring.model.Deployment;
import ai.lumina.monitoring.service.DeploymentService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * REST controller for managing deployments in the monitoring system.
 */
@RestController
@RequestMapping("/api/deployments")
@RequiredArgsConstructor
public class DeploymentController {

    private final DeploymentService deploymentService;

    /**
     * Prepare a deployment.
     *
     * @param request The deployment request
     * @return The prepared deployment
     */
    @PostMapping("/prepare")
    public ResponseEntity<Deployment> prepareDeployment(@RequestBody DeploymentPrepareRequest request) {
        Deployment deployment = deploymentService.prepareDeployment(
                request.getServiceName(),
                request.getVersion(),
                request.getEnvironment(),
                request.getArtifactPath(),
                request.getArtifactChecksum(),
                request.getDeploymentStrategy(),
                request.getProperties()
        );
        return ResponseEntity.ok(deployment);
    }

    /**
     * Start a deployment.
     *
     * @param deploymentId The ID of the deployment
     * @return The updated deployment
     */
    @PostMapping("/{deploymentId}/start")
    public ResponseEntity<Deployment> startDeployment(@PathVariable String deploymentId) {
        Deployment deployment = deploymentService.startDeployment(deploymentId);
        return ResponseEntity.ok(deployment);
    }

    /**
     * Complete a deployment.
     *
     * @param deploymentId The ID of the deployment
     * @return The updated deployment
     */
    @PostMapping("/{deploymentId}/complete")
    public ResponseEntity<Deployment> completeDeployment(@PathVariable String deploymentId) {
        Deployment deployment = deploymentService.completeDeployment(deploymentId);
        return ResponseEntity.ok(deployment);
    }

    /**
     * Fail a deployment.
     *
     * @param deploymentId The ID of the deployment
     * @param request The deployment fail request
     * @return The updated deployment
     */
    @PostMapping("/{deploymentId}/fail")
    public ResponseEntity<Deployment> failDeployment(
            @PathVariable String deploymentId,
            @RequestBody DeploymentFailRequest request) {
        Deployment deployment = deploymentService.failDeployment(deploymentId, request.getError());
        return ResponseEntity.ok(deployment);
    }

    /**
     * Get a deployment by ID.
     *
     * @param deploymentId The ID of the deployment
     * @return The deployment
     */
    @GetMapping("/{deploymentId}")
    public ResponseEntity<Deployment> getDeploymentById(@PathVariable String deploymentId) {
        return ResponseEntity.ok(deploymentService.getDeploymentById(deploymentId));
    }

    /**
     * Get deployments by service name.
     *
     * @param serviceName The name of the service
     * @return List of deployments for the given service
     */
    @GetMapping("/service/{serviceName}")
    public ResponseEntity<List<Deployment>> getDeploymentsByServiceName(@PathVariable String serviceName) {
        return ResponseEntity.ok(deploymentService.getDeploymentsByServiceName(serviceName));
    }

    /**
     * Get deployments by environment.
     *
     * @param environment The environment of the deployment
     * @return List of deployments for the given environment
     */
    @GetMapping("/environment/{environment}")
    public ResponseEntity<List<Deployment>> getDeploymentsByEnvironment(@PathVariable String environment) {
        return ResponseEntity.ok(deploymentService.getDeploymentsByEnvironment(environment));
    }

    /**
     * Get deployments by status.
     *
     * @param status The status of the deployment
     * @return List of deployments with the given status
     */
    @GetMapping("/status/{status}")
    public ResponseEntity<List<Deployment>> getDeploymentsByStatus(@PathVariable String status) {
        return ResponseEntity.ok(deploymentService.getDeploymentsByStatus(status));
    }

    /**
     * Get deployments by service name and environment.
     *
     * @param serviceName The name of the service
     * @param environment The environment of the deployment
     * @return List of deployments for the given service and environment
     */
    @GetMapping("/service/{serviceName}/environment/{environment}")
    public ResponseEntity<List<Deployment>> getDeploymentsByServiceAndEnvironment(
            @PathVariable String serviceName,
            @PathVariable String environment) {
        return ResponseEntity.ok(deploymentService.getDeploymentsByServiceAndEnvironment(serviceName, environment));
    }

    /**
     * Get deployments within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of deployments within the time range
     */
    @GetMapping("/timerange")
    public ResponseEntity<List<Deployment>> getDeploymentsInTimeRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(deploymentService.getDeploymentsInTimeRange(startTime, endTime));
    }

    /**
     * Get the most recent deployment for a service in an environment.
     *
     * @param serviceName The name of the service
     * @param environment The environment of the deployment
     * @return The most recent deployment for the service in the environment
     */
    @GetMapping("/service/{serviceName}/environment/{environment}/latest")
    public ResponseEntity<Deployment> getMostRecentDeployment(
            @PathVariable String serviceName,
            @PathVariable String environment) {
        return ResponseEntity.ok(deploymentService.getMostRecentDeployment(serviceName, environment));
    }

    /**
     * Count deployments by status within a time range.
     *
     * @param status The status of the deployment
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of deployments with the given status within the time range
     */
    @GetMapping("/status/{status}/count")
    public ResponseEntity<Long> countDeploymentsByStatus(
            @PathVariable String status,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(deploymentService.countDeploymentsByStatus(status, startTime, endTime));
    }

    /**
     * Calculate the average deployment duration by environment.
     *
     * @param environment The environment of the deployment
     * @return The average deployment duration in seconds
     */
    @GetMapping("/environment/{environment}/average-duration")
    public ResponseEntity<Double> calculateAverageDeploymentDuration(@PathVariable String environment) {
        return ResponseEntity.ok(deploymentService.calculateAverageDeploymentDuration(environment));
    }

    /**
     * Calculate the deployment success rate by environment within a time range.
     *
     * @param environment The environment of the deployment
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The deployment success rate (percentage)
     */
    @GetMapping("/environment/{environment}/success-rate")
    public ResponseEntity<Double> calculateDeploymentSuccessRate(
            @PathVariable String environment,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(deploymentService.calculateDeploymentSuccessRate(environment, startTime, endTime));
    }

    /**
     * Request object for preparing a deployment.
     */
    public static class DeploymentPrepareRequest {
        private String serviceName;
        private String version;
        private String environment;
        private String artifactPath;
        private String artifactChecksum;
        private String deploymentStrategy;
        private Map<String, String> properties;

        public String getServiceName() {
            return serviceName;
        }

        public void setServiceName(String serviceName) {
            this.serviceName = serviceName;
        }

        public String getVersion() {
            return version;
        }

        public void setVersion(String version) {
            this.version = version;
        }

        public String getEnvironment() {
            return environment;
        }

        public void setEnvironment(String environment) {
            this.environment = environment;
        }

        public String getArtifactPath() {
            return artifactPath;
        }

        public void setArtifactPath(String artifactPath) {
            this.artifactPath = artifactPath;
        }

        public String getArtifactChecksum() {
            return artifactChecksum;
        }

        public void setArtifactChecksum(String artifactChecksum) {
            this.artifactChecksum = artifactChecksum;
        }

        public String getDeploymentStrategy() {
            return deploymentStrategy;
        }

        public void setDeploymentStrategy(String deploymentStrategy) {
            this.deploymentStrategy = deploymentStrategy;
        }

        public Map<String, String> getProperties() {
            return properties;
        }

        public void setProperties(Map<String, String> properties) {
            this.properties = properties;
        }
    }

    /**
     * Request object for failing a deployment.
     */
    public static class DeploymentFailRequest {
        private String error;

        public String getError() {
            return error;
        }

        public void setError(String error) {
            this.error = error;
        }
    }
}
