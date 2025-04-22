package ai.lumina.monitoring.service;

import ai.lumina.monitoring.model.HealthCheck;
import ai.lumina.monitoring.repository.HealthCheckRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

/**
 * Service for managing health checks in the monitoring system.
 * This service provides functionality for performing, storing, and querying health checks.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class HealthCheckService {

    private final HealthCheckRepository healthCheckRepository;

    /**
     * Record a health check result.
     *
     * @param componentName The name of the component
     * @param componentType The type of the component
     * @param status The status of the health check
     * @param responseTimeMs The response time in milliseconds
     * @param message The message for the health check
     * @param details The details of the health check
     * @return The saved health check
     */
    @Transactional
    public HealthCheck recordHealthCheck(String componentName, String componentType, String status, 
                                        Long responseTimeMs, String message, 
                                        List<HealthCheck.HealthCheckDetail> details) {
        HealthCheck healthCheck = HealthCheck.builder()
                .componentName(componentName)
                .componentType(componentType)
                .status(status)
                .timestamp(Instant.now())
                .responseTimeMs(responseTimeMs)
                .message(message)
                .details(details != null ? details : new ArrayList<>())
                .build();
        
        log.debug("Recording health check: {}", healthCheck);
        return healthCheckRepository.save(healthCheck);
    }

    /**
     * Get health checks by component name.
     *
     * @param componentName The name of the component
     * @return List of health checks for the given component
     */
    @Transactional(readOnly = true)
    public List<HealthCheck> getHealthChecksByComponentName(String componentName) {
        return healthCheckRepository.findByComponentName(componentName);
    }

    /**
     * Get health checks by component type.
     *
     * @param componentType The type of the component
     * @return List of health checks for the given component type
     */
    @Transactional(readOnly = true)
    public List<HealthCheck> getHealthChecksByComponentType(String componentType) {
        return healthCheckRepository.findByComponentType(componentType);
    }

    /**
     * Get health checks by status.
     *
     * @param status The status of the health check
     * @return List of health checks with the given status
     */
    @Transactional(readOnly = true)
    public List<HealthCheck> getHealthChecksByStatus(String status) {
        return healthCheckRepository.findByStatus(status);
    }

    /**
     * Get health checks within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of health checks within the time range
     */
    @Transactional(readOnly = true)
    public List<HealthCheck> getHealthChecksInTimeRange(Instant startTime, Instant endTime) {
        return healthCheckRepository.findByTimestampBetween(startTime, endTime);
    }

    /**
     * Get the most recent health check for a component.
     *
     * @param componentName The name of the component
     * @return The most recent health check for the component
     */
    @Transactional(readOnly = true)
    public HealthCheck getMostRecentHealthCheck(String componentName) {
        return healthCheckRepository.findFirstByComponentNameOrderByTimestampDesc(componentName);
    }

    /**
     * Get the most recent health checks for all components.
     *
     * @return List of the most recent health check for each component
     */
    @Transactional(readOnly = true)
    public List<HealthCheck> getMostRecentHealthChecksForAllComponents() {
        return healthCheckRepository.findMostRecentHealthChecksForAllComponents();
    }

    /**
     * Count health checks by status within a time range.
     *
     * @param status The status of the health check
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of health checks with the given status within the time range
     */
    @Transactional(readOnly = true)
    public Long countHealthChecksByStatus(String status, Instant startTime, Instant endTime) {
        return healthCheckRepository.countByStatusAndTimeRange(status, startTime, endTime);
    }

    /**
     * Calculate the average response time for a component within a time range.
     *
     * @param componentName The name of the component
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average response time for the component
     */
    @Transactional(readOnly = true)
    public Double calculateAverageResponseTime(String componentName, Instant startTime, Instant endTime) {
        return healthCheckRepository.calculateAverageResponseTimeByComponentAndTimeRange(componentName, startTime, endTime);
    }

    /**
     * Delete health checks older than a specified time.
     *
     * @param cutoffTime The cutoff time
     * @return The number of health checks deleted
     */
    @Transactional
    public long deleteHealthChecksOlderThan(Instant cutoffTime) {
        List<HealthCheck> oldHealthChecks = healthCheckRepository.findAll().stream()
                .filter(healthCheck -> healthCheck.getTimestamp().isBefore(cutoffTime))
                .toList();
        
        if (!oldHealthChecks.isEmpty()) {
            healthCheckRepository.deleteAll(oldHealthChecks);
            log.info("Deleted {} health checks older than {}", oldHealthChecks.size(), cutoffTime);
        }
        
        return oldHealthChecks.size();
    }
}
