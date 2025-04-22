package ai.lumina.monitoring.controller;

import ai.lumina.monitoring.model.PerformanceProfile;
import ai.lumina.monitoring.service.PerformanceService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * REST controller for managing performance profiles in the monitoring system.
 */
@RestController
@RequestMapping("/api/performance")
@RequiredArgsConstructor
public class PerformanceController {

    private final PerformanceService performanceService;

    /**
     * Record a performance profile.
     *
     * @param request The performance profile request
     * @return The saved performance profile
     */
    @PostMapping
    public ResponseEntity<PerformanceProfile> recordPerformanceProfile(@RequestBody PerformanceProfileRequest request) {
        PerformanceProfile profile = performanceService.recordPerformanceProfile(
                request.getOperationName(),
                request.getServiceName(),
                request.getDurationMs(),
                request.getCpuPercent(),
                request.getMemoryBytes(),
                request.getMemoryDeltaBytes(),
                request.getError(),
                request.getAttributes()
        );
        return ResponseEntity.ok(profile);
    }

    /**
     * Get performance profiles by operation name.
     *
     * @param operationName The name of the operation
     * @return List of performance profiles for the given operation
     */
    @GetMapping("/operation/{operationName}")
    public ResponseEntity<List<PerformanceProfile>> getProfilesByOperationName(@PathVariable String operationName) {
        return ResponseEntity.ok(performanceService.getProfilesByOperationName(operationName));
    }

    /**
     * Get performance profiles by service name.
     *
     * @param serviceName The name of the service
     * @return List of performance profiles for the given service
     */
    @GetMapping("/service/{serviceName}")
    public ResponseEntity<List<PerformanceProfile>> getProfilesByServiceName(@PathVariable String serviceName) {
        return ResponseEntity.ok(performanceService.getProfilesByServiceName(serviceName));
    }

    /**
     * Get performance profiles by operation name and service name.
     *
     * @param operationName The name of the operation
     * @param serviceName The name of the service
     * @return List of performance profiles for the given operation and service
     */
    @GetMapping("/operation/{operationName}/service/{serviceName}")
    public ResponseEntity<List<PerformanceProfile>> getProfilesByOperationAndService(
            @PathVariable String operationName,
            @PathVariable String serviceName) {
        return ResponseEntity.ok(performanceService.getProfilesByOperationAndService(operationName, serviceName));
    }

    /**
     * Get performance profiles within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of performance profiles within the time range
     */
    @GetMapping("/timerange")
    public ResponseEntity<List<PerformanceProfile>> getProfilesInTimeRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(performanceService.getProfilesInTimeRange(startTime, endTime));
    }

    /**
     * Get slow performance profiles (duration greater than threshold).
     *
     * @param thresholdMs The duration threshold in milliseconds
     * @return List of performance profiles with duration greater than the threshold
     */
    @GetMapping("/slow")
    public ResponseEntity<List<PerformanceProfile>> getSlowProfiles(@RequestParam double thresholdMs) {
        return ResponseEntity.ok(performanceService.getSlowProfiles(thresholdMs));
    }

    /**
     * Get performance profiles with errors.
     *
     * @return List of performance profiles with errors
     */
    @GetMapping("/errors")
    public ResponseEntity<List<PerformanceProfile>> getProfilesWithErrors() {
        return ResponseEntity.ok(performanceService.getProfilesWithErrors());
    }

    /**
     * Calculate the average duration for an operation.
     *
     * @param operationName The name of the operation
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average duration in milliseconds
     */
    @GetMapping("/operation/{operationName}/average-duration")
    public ResponseEntity<Double> calculateAverageDuration(
            @PathVariable String operationName,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(performanceService.calculateAverageDuration(operationName, startTime, endTime));
    }

    /**
     * Calculate the 95th percentile duration for an operation.
     *
     * @param operationName The name of the operation
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The 95th percentile duration in milliseconds
     */
    @GetMapping("/operation/{operationName}/p95-duration")
    public ResponseEntity<Double> calculate95thPercentileDuration(
            @PathVariable String operationName,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(performanceService.calculate95thPercentileDuration(operationName, startTime, endTime));
    }

    /**
     * Calculate the average CPU usage for an operation.
     *
     * @param operationName The name of the operation
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average CPU usage percentage
     */
    @GetMapping("/operation/{operationName}/average-cpu")
    public ResponseEntity<Double> calculateAverageCpuUsage(
            @PathVariable String operationName,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(performanceService.calculateAverageCpuUsage(operationName, startTime, endTime));
    }

    /**
     * Calculate the average memory usage for an operation.
     *
     * @param operationName The name of the operation
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average memory usage in bytes
     */
    @GetMapping("/operation/{operationName}/average-memory")
    public ResponseEntity<Double> calculateAverageMemoryUsage(
            @PathVariable String operationName,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(performanceService.calculateAverageMemoryUsage(operationName, startTime, endTime));
    }

    /**
     * Delete performance profiles older than a specified time.
     *
     * @param cutoffTime The cutoff time
     * @return The number of performance profiles deleted
     */
    @DeleteMapping("/cleanup")
    public ResponseEntity<Long> deleteProfilesOlderThan(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant cutoffTime) {
        return ResponseEntity.ok(performanceService.deleteProfilesOlderThan(cutoffTime));
    }

    /**
     * Request object for recording a performance profile.
     */
    public static class PerformanceProfileRequest {
        private String operationName;
        private String serviceName;
        private Double durationMs;
        private Double cpuPercent;
        private Long memoryBytes;
        private Long memoryDeltaBytes;
        private Boolean error;
        private Map<String, String> attributes;

        public String getOperationName() {
            return operationName;
        }

        public void setOperationName(String operationName) {
            this.operationName = operationName;
        }

        public String getServiceName() {
            return serviceName;
        }

        public void setServiceName(String serviceName) {
            this.serviceName = serviceName;
        }

        public Double getDurationMs() {
            return durationMs;
        }

        public void setDurationMs(Double durationMs) {
            this.durationMs = durationMs;
        }

        public Double getCpuPercent() {
            return cpuPercent;
        }

        public void setCpuPercent(Double cpuPercent) {
            this.cpuPercent = cpuPercent;
        }

        public Long getMemoryBytes() {
            return memoryBytes;
        }

        public void setMemoryBytes(Long memoryBytes) {
            this.memoryBytes = memoryBytes;
        }

        public Long getMemoryDeltaBytes() {
            return memoryDeltaBytes;
        }

        public void setMemoryDeltaBytes(Long memoryDeltaBytes) {
            this.memoryDeltaBytes = memoryDeltaBytes;
        }

        public Boolean getError() {
            return error;
        }

        public void setError(Boolean error) {
            this.error = error;
        }

        public Map<String, String> getAttributes() {
            return attributes;
        }

        public void setAttributes(Map<String, String> attributes) {
            this.attributes = attributes;
        }
    }
}
