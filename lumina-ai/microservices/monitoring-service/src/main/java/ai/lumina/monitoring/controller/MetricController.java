package ai.lumina.monitoring.controller;

import ai.lumina.monitoring.model.Metric;
import ai.lumina.monitoring.service.MetricService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * REST controller for managing metrics in the monitoring system.
 */
@RestController
@RequestMapping("/api/metrics")
@RequiredArgsConstructor
public class MetricController {

    private final MetricService metricService;

    /**
     * Record a new metric.
     *
     * @param request The metric request
     * @return The created metric
     */
    @PostMapping
    public ResponseEntity<Metric> recordMetric(@RequestBody MetricRequest request) {
        Metric metric = metricService.recordMetric(
                request.getName(),
                request.getValue(),
                request.getUnit(),
                request.getSource(),
                request.getLabels()
        );
        return ResponseEntity.ok(metric);
    }

    /**
     * Get metrics by name.
     *
     * @param name The name of the metric
     * @return List of metrics with the given name
     */
    @GetMapping("/name/{name}")
    public ResponseEntity<List<Metric>> getMetricsByName(@PathVariable String name) {
        return ResponseEntity.ok(metricService.getMetricsByName(name));
    }

    /**
     * Get metrics by source.
     *
     * @param source The source of the metric
     * @return List of metrics from the given source
     */
    @GetMapping("/source/{source}")
    public ResponseEntity<List<Metric>> getMetricsBySource(@PathVariable String source) {
        return ResponseEntity.ok(metricService.getMetricsBySource(source));
    }

    /**
     * Get metrics by name and source.
     *
     * @param name The name of the metric
     * @param source The source of the metric
     * @return List of metrics with the given name and source
     */
    @GetMapping("/name/{name}/source/{source}")
    public ResponseEntity<List<Metric>> getMetricsByNameAndSource(
            @PathVariable String name,
            @PathVariable String source) {
        return ResponseEntity.ok(metricService.getMetricsByNameAndSource(name, source));
    }

    /**
     * Get metrics within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of metrics within the time range
     */
    @GetMapping("/timerange")
    public ResponseEntity<List<Metric>> getMetricsInTimeRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(metricService.getMetricsInTimeRange(startTime, endTime));
    }

    /**
     * Calculate the average value of a metric by name within a time range.
     *
     * @param name The name of the metric
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average value of the metric
     */
    @GetMapping("/name/{name}/average")
    public ResponseEntity<Double> calculateAverageMetricValue(
            @PathVariable String name,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(metricService.calculateAverageMetricValue(name, startTime, endTime));
    }

    /**
     * Calculate the maximum value of a metric by name within a time range.
     *
     * @param name The name of the metric
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The maximum value of the metric
     */
    @GetMapping("/name/{name}/max")
    public ResponseEntity<Double> calculateMaxMetricValue(
            @PathVariable String name,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(metricService.calculateMaxMetricValue(name, startTime, endTime));
    }

    /**
     * Calculate the minimum value of a metric by name within a time range.
     *
     * @param name The name of the metric
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The minimum value of the metric
     */
    @GetMapping("/name/{name}/min")
    public ResponseEntity<Double> calculateMinMetricValue(
            @PathVariable String name,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(metricService.calculateMinMetricValue(name, startTime, endTime));
    }

    /**
     * Delete metrics older than a specified time.
     *
     * @param cutoffTime The cutoff time
     * @return The number of metrics deleted
     */
    @DeleteMapping("/cleanup")
    public ResponseEntity<Long> deleteMetricsOlderThan(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant cutoffTime) {
        return ResponseEntity.ok(metricService.deleteMetricsOlderThan(cutoffTime));
    }

    /**
     * Request object for recording a metric.
     */
    public static class MetricRequest {
        private String name;
        private Double value;
        private String unit;
        private String source;
        private Map<String, String> labels;

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public Double getValue() {
            return value;
        }

        public void setValue(Double value) {
            this.value = value;
        }

        public String getUnit() {
            return unit;
        }

        public void setUnit(String unit) {
            this.unit = unit;
        }

        public String getSource() {
            return source;
        }

        public void setSource(String source) {
            this.source = source;
        }

        public Map<String, String> getLabels() {
            return labels;
        }

        public void setLabels(Map<String, String> labels) {
            this.labels = labels;
        }
    }
}
