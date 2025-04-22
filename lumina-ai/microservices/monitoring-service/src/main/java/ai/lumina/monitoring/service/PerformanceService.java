package ai.lumina.monitoring.service;

import ai.lumina.monitoring.model.PerformanceProfile;
import ai.lumina.monitoring.repository.PerformanceProfileRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Service for managing performance profiles in the monitoring system.
 * This service provides functionality for recording, analyzing, and querying performance data.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class PerformanceService {

    private final PerformanceProfileRepository performanceProfileRepository;

    /**
     * Record a performance profile.
     *
     * @param operationName The name of the operation
     * @param serviceName The name of the service
     * @param durationMs The duration in milliseconds
     * @param cpuPercent The CPU usage percentage
     * @param memoryBytes The memory usage in bytes
     * @param memoryDeltaBytes The memory change in bytes
     * @param error Whether an error occurred
     * @param attributes Additional attributes
     * @return The saved performance profile
     */
    @Transactional
    public PerformanceProfile recordPerformanceProfile(String operationName, String serviceName,
                                                     Double durationMs, Double cpuPercent,
                                                     Long memoryBytes, Long memoryDeltaBytes,
                                                     Boolean error, Map<String, String> attributes) {
        PerformanceProfile profile = PerformanceProfile.builder()
                .operationName(operationName)
                .serviceName(serviceName)
                .timestamp(Instant.now())
                .durationMs(durationMs)
                .cpuPercent(cpuPercent)
                .memoryBytes(memoryBytes)
                .memoryDeltaBytes(memoryDeltaBytes)
                .error(error)
                .attributes(attributes != null ? attributes : new HashMap<>())
                .build();
        
        log.debug("Recording performance profile: {}", profile);
        return performanceProfileRepository.save(profile);
    }

    /**
     * Get performance profiles by operation name.
     *
     * @param operationName The name of the operation
     * @return List of performance profiles for the given operation
     */
    @Transactional(readOnly = true)
    public List<PerformanceProfile> getProfilesByOperationName(String operationName) {
        return performanceProfileRepository.findByOperationName(operationName);
    }

    /**
     * Get performance profiles by service name.
     *
     * @param serviceName The name of the service
     * @return List of performance profiles for the given service
     */
    @Transactional(readOnly = true)
    public List<PerformanceProfile> getProfilesByServiceName(String serviceName) {
        return performanceProfileRepository.findByServiceName(serviceName);
    }

    /**
     * Get performance profiles by operation name and service name.
     *
     * @param operationName The name of the operation
     * @param serviceName The name of the service
     * @return List of performance profiles for the given operation and service
     */
    @Transactional(readOnly = true)
    public List<PerformanceProfile> getProfilesByOperationAndService(String operationName, String serviceName) {
        return performanceProfileRepository.findByOperationNameAndServiceName(operationName, serviceName);
    }

    /**
     * Get performance profiles within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of performance profiles within the time range
     */
    @Transactional(readOnly = true)
    public List<PerformanceProfile> getProfilesInTimeRange(Instant startTime, Instant endTime) {
        return performanceProfileRepository.findByTimestampBetween(startTime, endTime);
    }

    /**
     * Get slow performance profiles (duration greater than threshold).
     *
     * @param thresholdMs The duration threshold in milliseconds
     * @return List of performance profiles with duration greater than the threshold
     */
    @Transactional(readOnly = true)
    public List<PerformanceProfile> getSlowProfiles(double thresholdMs) {
        return performanceProfileRepository.findByDurationMsGreaterThan(thresholdMs);
    }

    /**
     * Get performance profiles with errors.
     *
     * @return List of performance profiles with errors
     */
    @Transactional(readOnly = true)
    public List<PerformanceProfile> getProfilesWithErrors() {
        return performanceProfileRepository.findByErrorTrue();
    }

    /**
     * Calculate the average duration for an operation.
     *
     * @param operationName The name of the operation
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average duration in milliseconds
     */
    @Transactional(readOnly = true)
    public Double calculateAverageDuration(String operationName, Instant startTime, Instant endTime) {
        return performanceProfileRepository.calculateAverageDurationByOperationAndTimeRange(operationName, startTime, endTime);
    }

    /**
     * Calculate the 95th percentile duration for an operation.
     *
     * @param operationName The name of the operation
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The 95th percentile duration in milliseconds
     */
    @Transactional(readOnly = true)
    public Double calculate95thPercentileDuration(String operationName, Instant startTime, Instant endTime) {
        return performanceProfileRepository.calculate95thPercentileDurationByOperationAndTimeRange(operationName, startTime, endTime);
    }

    /**
     * Calculate the average CPU usage for an operation.
     *
     * @param operationName The name of the operation
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average CPU usage percentage
     */
    @Transactional(readOnly = true)
    public Double calculateAverageCpuUsage(String operationName, Instant startTime, Instant endTime) {
        return performanceProfileRepository.calculateAverageCpuUsageByOperationAndTimeRange(operationName, startTime, endTime);
    }

    /**
     * Calculate the average memory usage for an operation.
     *
     * @param operationName The name of the operation
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average memory usage in bytes
     */
    @Transactional(readOnly = true)
    public Double calculateAverageMemoryUsage(String operationName, Instant startTime, Instant endTime) {
        return performanceProfileRepository.calculateAverageMemoryUsageByOperationAndTimeRange(operationName, startTime, endTime);
    }

    /**
     * Delete performance profiles older than a specified time.
     *
     * @param cutoffTime The cutoff time
     * @return The number of performance profiles deleted
     */
    @Transactional
    public long deleteProfilesOlderThan(Instant cutoffTime) {
        List<PerformanceProfile> oldProfiles = performanceProfileRepository.findAll().stream()
                .filter(profile -> profile.getTimestamp().isBefore(cutoffTime))
                .toList();
        
        if (!oldProfiles.isEmpty()) {
            performanceProfileRepository.deleteAll(oldProfiles);
            log.info("Deleted {} performance profiles older than {}", oldProfiles.size(), cutoffTime);
        }
        
        return oldProfiles.size();
    }
}
