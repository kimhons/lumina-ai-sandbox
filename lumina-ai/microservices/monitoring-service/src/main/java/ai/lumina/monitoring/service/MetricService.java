package ai.lumina.monitoring.service;

import ai.lumina.monitoring.model.Metric;
import ai.lumina.monitoring.repository.MetricRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Service for managing metrics in the monitoring system.
 * This service provides functionality for collecting, storing, and querying metrics.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class MetricService {

    private final MetricRepository metricRepository;

    /**
     * Record a new metric.
     *
     * @param name The name of the metric
     * @param value The value of the metric
     * @param unit The unit of measurement
     * @param source The source of the metric
     * @param labels Additional labels for the metric
     * @return The saved metric
     */
    @Transactional
    public Metric recordMetric(String name, Double value, String unit, String source, Map<String, String> labels) {
        Metric metric = Metric.builder()
                .name(name)
                .value(value)
                .unit(unit)
                .source(source)
                .timestamp(Instant.now())
                .labels(labels != null ? labels : new HashMap<>())
                .build();
        
        log.debug("Recording metric: {}", metric);
        return metricRepository.save(metric);
    }

    /**
     * Get metrics by name.
     *
     * @param name The name of the metric
     * @return List of metrics with the given name
     */
    @Transactional(readOnly = true)
    public List<Metric> getMetricsByName(String name) {
        return metricRepository.findByName(name);
    }

    /**
     * Get metrics by source.
     *
     * @param source The source of the metric
     * @return List of metrics from the given source
     */
    @Transactional(readOnly = true)
    public List<Metric> getMetricsBySource(String source) {
        return metricRepository.findBySource(source);
    }

    /**
     * Get metrics by name and source.
     *
     * @param name The name of the metric
     * @param source The source of the metric
     * @return List of metrics with the given name and source
     */
    @Transactional(readOnly = true)
    public List<Metric> getMetricsByNameAndSource(String name, String source) {
        return metricRepository.findByNameAndSource(name, source);
    }

    /**
     * Get metrics within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of metrics within the time range
     */
    @Transactional(readOnly = true)
    public List<Metric> getMetricsInTimeRange(Instant startTime, Instant endTime) {
        return metricRepository.findByTimestampBetween(startTime, endTime);
    }

    /**
     * Get metrics by name within a time range.
     *
     * @param name The name of the metric
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of metrics with the given name within the time range
     */
    @Transactional(readOnly = true)
    public List<Metric> getMetricsByNameInTimeRange(String name, Instant startTime, Instant endTime) {
        return metricRepository.findByNameAndTimestampBetween(name, startTime, endTime);
    }

    /**
     * Calculate the average value of a metric by name within a time range.
     *
     * @param name The name of the metric
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average value of the metric
     */
    @Transactional(readOnly = true)
    public Double calculateAverageMetricValue(String name, Instant startTime, Instant endTime) {
        return metricRepository.calculateAverageByNameAndTimeRange(name, startTime, endTime);
    }

    /**
     * Calculate the maximum value of a metric by name within a time range.
     *
     * @param name The name of the metric
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The maximum value of the metric
     */
    @Transactional(readOnly = true)
    public Double calculateMaxMetricValue(String name, Instant startTime, Instant endTime) {
        return metricRepository.calculateMaxByNameAndTimeRange(name, startTime, endTime);
    }

    /**
     * Calculate the minimum value of a metric by name within a time range.
     *
     * @param name The name of the metric
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The minimum value of the metric
     */
    @Transactional(readOnly = true)
    public Double calculateMinMetricValue(String name, Instant startTime, Instant endTime) {
        return metricRepository.calculateMinByNameAndTimeRange(name, startTime, endTime);
    }

    /**
     * Delete metrics older than a specified time.
     *
     * @param cutoffTime The cutoff time
     * @return The number of metrics deleted
     */
    @Transactional
    public long deleteMetricsOlderThan(Instant cutoffTime) {
        List<Metric> oldMetrics = metricRepository.findAll().stream()
                .filter(metric -> metric.getTimestamp().isBefore(cutoffTime))
                .toList();
        
        if (!oldMetrics.isEmpty()) {
            metricRepository.deleteAll(oldMetrics);
            log.info("Deleted {} metrics older than {}", oldMetrics.size(), cutoffTime);
        }
        
        return oldMetrics.size();
    }
}
