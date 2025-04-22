package ai.lumina.monitoring.controller;

import ai.lumina.monitoring.model.HealthCheck;
import ai.lumina.monitoring.service.HealthCheckService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;

/**
 * REST controller for managing health checks in the monitoring system.
 */
@RestController
@RequestMapping("/api/health-checks")
@RequiredArgsConstructor
public class HealthCheckController {

    private final HealthCheckService healthCheckService;

    /**
     * Record a health check result.
     *
     * @param request The health check request
     * @return The saved health check
     */
    @PostMapping
    public ResponseEntity<HealthCheck> recordHealthCheck(@RequestBody HealthCheckRequest request) {
        HealthCheck healthCheck = healthCheckService.recordHealthCheck(
                request.getComponentName(),
                request.getComponentType(),
                request.getStatus(),
                request.getResponseTimeMs(),
                request.getMessage(),
                request.getDetails()
        );
        return ResponseEntity.ok(healthCheck);
    }

    /**
     * Get health checks by component name.
     *
     * @param componentName The name of the component
     * @return List of health checks for the given component
     */
    @GetMapping("/component/{componentName}")
    public ResponseEntity<List<HealthCheck>> getHealthChecksByComponentName(@PathVariable String componentName) {
        return ResponseEntity.ok(healthCheckService.getHealthChecksByComponentName(componentName));
    }

    /**
     * Get health checks by component type.
     *
     * @param componentType The type of the component
     * @return List of health checks for the given component type
     */
    @GetMapping("/type/{componentType}")
    public ResponseEntity<List<HealthCheck>> getHealthChecksByComponentType(@PathVariable String componentType) {
        return ResponseEntity.ok(healthCheckService.getHealthChecksByComponentType(componentType));
    }

    /**
     * Get health checks by status.
     *
     * @param status The status of the health check
     * @return List of health checks with the given status
     */
    @GetMapping("/status/{status}")
    public ResponseEntity<List<HealthCheck>> getHealthChecksByStatus(@PathVariable String status) {
        return ResponseEntity.ok(healthCheckService.getHealthChecksByStatus(status));
    }

    /**
     * Get health checks within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of health checks within the time range
     */
    @GetMapping("/timerange")
    public ResponseEntity<List<HealthCheck>> getHealthChecksInTimeRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(healthCheckService.getHealthChecksInTimeRange(startTime, endTime));
    }

    /**
     * Get the most recent health check for a component.
     *
     * @param componentName The name of the component
     * @return The most recent health check for the component
     */
    @GetMapping("/component/{componentName}/latest")
    public ResponseEntity<HealthCheck> getMostRecentHealthCheck(@PathVariable String componentName) {
        return ResponseEntity.ok(healthCheckService.getMostRecentHealthCheck(componentName));
    }

    /**
     * Get the most recent health checks for all components.
     *
     * @return List of the most recent health check for each component
     */
    @GetMapping("/latest")
    public ResponseEntity<List<HealthCheck>> getMostRecentHealthChecksForAllComponents() {
        return ResponseEntity.ok(healthCheckService.getMostRecentHealthChecksForAllComponents());
    }

    /**
     * Count health checks by status within a time range.
     *
     * @param status The status of the health check
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of health checks with the given status within the time range
     */
    @GetMapping("/status/{status}/count")
    public ResponseEntity<Long> countHealthChecksByStatus(
            @PathVariable String status,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(healthCheckService.countHealthChecksByStatus(status, startTime, endTime));
    }

    /**
     * Calculate the average response time for a component within a time range.
     *
     * @param componentName The name of the component
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average response time for the component
     */
    @GetMapping("/component/{componentName}/average-response-time")
    public ResponseEntity<Double> calculateAverageResponseTime(
            @PathVariable String componentName,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(healthCheckService.calculateAverageResponseTime(componentName, startTime, endTime));
    }

    /**
     * Delete health checks older than a specified time.
     *
     * @param cutoffTime The cutoff time
     * @return The number of health checks deleted
     */
    @DeleteMapping("/cleanup")
    public ResponseEntity<Long> deleteHealthChecksOlderThan(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant cutoffTime) {
        return ResponseEntity.ok(healthCheckService.deleteHealthChecksOlderThan(cutoffTime));
    }

    /**
     * Request object for recording a health check.
     */
    public static class HealthCheckRequest {
        private String componentName;
        private String componentType;
        private String status;
        private Long responseTimeMs;
        private String message;
        private List<HealthCheck.HealthCheckDetail> details;

        public String getComponentName() {
            return componentName;
        }

        public void setComponentName(String componentName) {
            this.componentName = componentName;
        }

        public String getComponentType() {
            return componentType;
        }

        public void setComponentType(String componentType) {
            this.componentType = componentType;
        }

        public String getStatus() {
            return status;
        }

        public void setStatus(String status) {
            this.status = status;
        }

        public Long getResponseTimeMs() {
            return responseTimeMs;
        }

        public void setResponseTimeMs(Long responseTimeMs) {
            this.responseTimeMs = responseTimeMs;
        }

        public String getMessage() {
            return message;
        }

        public void setMessage(String message) {
            this.message = message;
        }

        public List<HealthCheck.HealthCheckDetail> getDetails() {
            return details;
        }

        public void setDetails(List<HealthCheck.HealthCheckDetail> details) {
            this.details = details;
        }
    }
}
