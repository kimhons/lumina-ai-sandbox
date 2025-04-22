package ai.lumina.monitoring.service;

import ai.lumina.monitoring.model.Trace;
import ai.lumina.monitoring.repository.TraceRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Service for managing distributed tracing in the monitoring system.
 * This service provides functionality for creating, storing, and querying traces.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class TraceService {

    private final TraceRepository traceRepository;

    /**
     * Start a new trace.
     *
     * @param name The name of the trace
     * @param serviceName The name of the service
     * @param attributes Additional attributes for the trace
     * @return The created trace
     */
    @Transactional
    public Trace startTrace(String name, String serviceName, Map<String, String> attributes) {
        String traceId = UUID.randomUUID().toString();
        Trace trace = Trace.builder()
                .id(traceId)
                .name(name)
                .serviceName(serviceName)
                .startTime(Instant.now())
                .attributes(attributes != null ? attributes : new HashMap<>())
                .build();
        
        log.debug("Starting trace: {}", trace);
        return traceRepository.save(trace);
    }

    /**
     * End a trace.
     *
     * @param traceId The ID of the trace
     * @param status The status of the trace
     * @return The updated trace
     */
    @Transactional
    public Trace endTrace(String traceId, String status) {
        Trace trace = traceRepository.findById(traceId)
                .orElseThrow(() -> new IllegalArgumentException("Trace not found: " + traceId));
        
        Instant endTime = Instant.now();
        long durationMs = endTime.toEpochMilli() - trace.getStartTime().toEpochMilli();
        
        trace.setEndTime(endTime);
        trace.setDurationMs(durationMs);
        trace.setStatus(status);
        
        log.debug("Ending trace: {}", trace);
        return traceRepository.save(trace);
    }

    /**
     * Get a trace by ID.
     *
     * @param traceId The ID of the trace
     * @return The trace
     */
    @Transactional(readOnly = true)
    public Trace getTraceById(String traceId) {
        return traceRepository.findById(traceId)
                .orElseThrow(() -> new IllegalArgumentException("Trace not found: " + traceId));
    }

    /**
     * Get traces by name.
     *
     * @param name The name of the trace
     * @return List of traces with the given name
     */
    @Transactional(readOnly = true)
    public List<Trace> getTracesByName(String name) {
        return traceRepository.findByName(name);
    }

    /**
     * Get traces by service name.
     *
     * @param serviceName The name of the service
     * @return List of traces from the given service
     */
    @Transactional(readOnly = true)
    public List<Trace> getTracesByServiceName(String serviceName) {
        return traceRepository.findByServiceName(serviceName);
    }

    /**
     * Get traces by status.
     *
     * @param status The status of the trace
     * @return List of traces with the given status
     */
    @Transactional(readOnly = true)
    public List<Trace> getTracesByStatus(String status) {
        return traceRepository.findByStatus(status);
    }

    /**
     * Get traces within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of traces within the time range
     */
    @Transactional(readOnly = true)
    public List<Trace> getTracesInTimeRange(Instant startTime, Instant endTime) {
        return traceRepository.findByStartTimeBetween(startTime, endTime);
    }

    /**
     * Get slow traces (duration greater than threshold).
     *
     * @param thresholdMs The duration threshold in milliseconds
     * @return List of traces with duration greater than the threshold
     */
    @Transactional(readOnly = true)
    public List<Trace> getSlowTraces(long thresholdMs) {
        return traceRepository.findByDurationMsGreaterThan(thresholdMs);
    }

    /**
     * Calculate the average duration for a trace name.
     *
     * @param name The name of the trace
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average duration in milliseconds
     */
    @Transactional(readOnly = true)
    public Double calculateAverageDuration(String name, Instant startTime, Instant endTime) {
        return traceRepository.calculateAverageDurationByNameAndTimeRange(name, startTime, endTime);
    }

    /**
     * Calculate the 95th percentile duration for a trace name.
     *
     * @param name The name of the trace
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The 95th percentile duration in milliseconds
     */
    @Transactional(readOnly = true)
    public Double calculate95thPercentileDuration(String name, Instant startTime, Instant endTime) {
        return traceRepository.calculate95thPercentileDurationByNameAndTimeRange(name, startTime, endTime);
    }

    /**
     * Delete traces older than a specified time.
     *
     * @param cutoffTime The cutoff time
     * @return The number of traces deleted
     */
    @Transactional
    public long deleteTracesOlderThan(Instant cutoffTime) {
        List<Trace> oldTraces = traceRepository.findAll().stream()
                .filter(trace -> trace.getStartTime().isBefore(cutoffTime))
                .toList();
        
        if (!oldTraces.isEmpty()) {
            traceRepository.deleteAll(oldTraces);
            log.info("Deleted {} traces older than {}", oldTraces.size(), cutoffTime);
        }
        
        return oldTraces.size();
    }
}
