package ai.lumina.monitoring.controller;

import ai.lumina.monitoring.model.Trace;
import ai.lumina.monitoring.service.TraceService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * REST controller for managing traces in the monitoring system.
 */
@RestController
@RequestMapping("/api/traces")
@RequiredArgsConstructor
public class TraceController {

    private final TraceService traceService;

    /**
     * Start a new trace.
     *
     * @param request The trace request
     * @return The created trace
     */
    @PostMapping("/start")
    public ResponseEntity<Trace> startTrace(@RequestBody TraceStartRequest request) {
        Trace trace = traceService.startTrace(
                request.getName(),
                request.getServiceName(),
                request.getAttributes()
        );
        return ResponseEntity.ok(trace);
    }

    /**
     * End a trace.
     *
     * @param traceId The ID of the trace
     * @param request The trace end request
     * @return The updated trace
     */
    @PostMapping("/{traceId}/end")
    public ResponseEntity<Trace> endTrace(
            @PathVariable String traceId,
            @RequestBody TraceEndRequest request) {
        Trace trace = traceService.endTrace(traceId, request.getStatus());
        return ResponseEntity.ok(trace);
    }

    /**
     * Get a trace by ID.
     *
     * @param traceId The ID of the trace
     * @return The trace
     */
    @GetMapping("/{traceId}")
    public ResponseEntity<Trace> getTraceById(@PathVariable String traceId) {
        return ResponseEntity.ok(traceService.getTraceById(traceId));
    }

    /**
     * Get traces by name.
     *
     * @param name The name of the trace
     * @return List of traces with the given name
     */
    @GetMapping("/name/{name}")
    public ResponseEntity<List<Trace>> getTracesByName(@PathVariable String name) {
        return ResponseEntity.ok(traceService.getTracesByName(name));
    }

    /**
     * Get traces by service name.
     *
     * @param serviceName The name of the service
     * @return List of traces from the given service
     */
    @GetMapping("/service/{serviceName}")
    public ResponseEntity<List<Trace>> getTracesByServiceName(@PathVariable String serviceName) {
        return ResponseEntity.ok(traceService.getTracesByServiceName(serviceName));
    }

    /**
     * Get traces by status.
     *
     * @param status The status of the trace
     * @return List of traces with the given status
     */
    @GetMapping("/status/{status}")
    public ResponseEntity<List<Trace>> getTracesByStatus(@PathVariable String status) {
        return ResponseEntity.ok(traceService.getTracesByStatus(status));
    }

    /**
     * Get traces within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of traces within the time range
     */
    @GetMapping("/timerange")
    public ResponseEntity<List<Trace>> getTracesInTimeRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(traceService.getTracesInTimeRange(startTime, endTime));
    }

    /**
     * Get slow traces (duration greater than threshold).
     *
     * @param thresholdMs The duration threshold in milliseconds
     * @return List of traces with duration greater than the threshold
     */
    @GetMapping("/slow")
    public ResponseEntity<List<Trace>> getSlowTraces(@RequestParam long thresholdMs) {
        return ResponseEntity.ok(traceService.getSlowTraces(thresholdMs));
    }

    /**
     * Calculate the average duration for a trace name.
     *
     * @param name The name of the trace
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average duration in milliseconds
     */
    @GetMapping("/name/{name}/average-duration")
    public ResponseEntity<Double> calculateAverageDuration(
            @PathVariable String name,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(traceService.calculateAverageDuration(name, startTime, endTime));
    }

    /**
     * Calculate the 95th percentile duration for a trace name.
     *
     * @param name The name of the trace
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The 95th percentile duration in milliseconds
     */
    @GetMapping("/name/{name}/p95-duration")
    public ResponseEntity<Double> calculate95thPercentileDuration(
            @PathVariable String name,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(traceService.calculate95thPercentileDuration(name, startTime, endTime));
    }

    /**
     * Delete traces older than a specified time.
     *
     * @param cutoffTime The cutoff time
     * @return The number of traces deleted
     */
    @DeleteMapping("/cleanup")
    public ResponseEntity<Long> deleteTracesOlderThan(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant cutoffTime) {
        return ResponseEntity.ok(traceService.deleteTracesOlderThan(cutoffTime));
    }

    /**
     * Request object for starting a trace.
     */
    public static class TraceStartRequest {
        private String name;
        private String serviceName;
        private Map<String, String> attributes;

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getServiceName() {
            return serviceName;
        }

        public void setServiceName(String serviceName) {
            this.serviceName = serviceName;
        }

        public Map<String, String> getAttributes() {
            return attributes;
        }

        public void setAttributes(Map<String, String> attributes) {
            this.attributes = attributes;
        }
    }

    /**
     * Request object for ending a trace.
     */
    public static class TraceEndRequest {
        private String status;

        public String getStatus() {
            return status;
        }

        public void setStatus(String status) {
            this.status = status;
        }
    }
}
