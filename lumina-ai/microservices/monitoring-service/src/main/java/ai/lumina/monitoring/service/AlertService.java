package ai.lumina.monitoring.service;

import ai.lumina.monitoring.model.Alert;
import ai.lumina.monitoring.repository.AlertRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Service for managing alerts in the monitoring system.
 * This service provides functionality for creating, updating, and querying alerts.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AlertService {

    private final AlertRepository alertRepository;

    /**
     * Create a new alert.
     *
     * @param name The name of the alert
     * @param severity The severity of the alert
     * @param source The source of the alert
     * @param description The description of the alert
     * @param rule The rule that triggered the alert
     * @param triggerValue The value that triggered the alert
     * @param thresholdValue The threshold value for the alert
     * @param labels Additional labels for the alert
     * @return The created alert
     */
    @Transactional
    public Alert createAlert(String name, String severity, String source, String description,
                           String rule, Double triggerValue, Double thresholdValue, Map<String, String> labels) {
        Alert alert = Alert.builder()
                .name(name)
                .severity(severity)
                .status("active")
                .source(source)
                .triggerTime(Instant.now())
                .description(description)
                .rule(rule)
                .triggerValue(triggerValue)
                .thresholdValue(thresholdValue)
                .labels(labels != null ? labels : new HashMap<>())
                .build();
        
        log.debug("Creating alert: {}", alert);
        return alertRepository.save(alert);
    }

    /**
     * Acknowledge an alert.
     *
     * @param alertId The ID of the alert
     * @return The updated alert
     */
    @Transactional
    public Alert acknowledgeAlert(Long alertId) {
        Alert alert = alertRepository.findById(alertId)
                .orElseThrow(() -> new IllegalArgumentException("Alert not found: " + alertId));
        
        alert.setStatus("acknowledged");
        
        log.debug("Acknowledging alert: {}", alert);
        return alertRepository.save(alert);
    }

    /**
     * Resolve an alert.
     *
     * @param alertId The ID of the alert
     * @return The updated alert
     */
    @Transactional
    public Alert resolveAlert(Long alertId) {
        Alert alert = alertRepository.findById(alertId)
                .orElseThrow(() -> new IllegalArgumentException("Alert not found: " + alertId));
        
        alert.setStatus("resolved");
        alert.setResolveTime(Instant.now());
        
        log.debug("Resolving alert: {}", alert);
        return alertRepository.save(alert);
    }

    /**
     * Get an alert by ID.
     *
     * @param alertId The ID of the alert
     * @return The alert
     */
    @Transactional(readOnly = true)
    public Alert getAlertById(Long alertId) {
        return alertRepository.findById(alertId)
                .orElseThrow(() -> new IllegalArgumentException("Alert not found: " + alertId));
    }

    /**
     * Get alerts by name.
     *
     * @param name The name of the alert
     * @return List of alerts with the given name
     */
    @Transactional(readOnly = true)
    public List<Alert> getAlertsByName(String name) {
        return alertRepository.findByName(name);
    }

    /**
     * Get alerts by severity.
     *
     * @param severity The severity of the alert
     * @return List of alerts with the given severity
     */
    @Transactional(readOnly = true)
    public List<Alert> getAlertsBySeverity(String severity) {
        return alertRepository.findBySeverity(severity);
    }

    /**
     * Get alerts by status.
     *
     * @param status The status of the alert
     * @return List of alerts with the given status
     */
    @Transactional(readOnly = true)
    public List<Alert> getAlertsByStatus(String status) {
        return alertRepository.findByStatus(status);
    }

    /**
     * Get alerts by source.
     *
     * @param source The source of the alert
     * @return List of alerts from the given source
     */
    @Transactional(readOnly = true)
    public List<Alert> getAlertsBySource(String source) {
        return alertRepository.findBySource(source);
    }

    /**
     * Get alerts within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of alerts within the time range
     */
    @Transactional(readOnly = true)
    public List<Alert> getAlertsInTimeRange(Instant startTime, Instant endTime) {
        return alertRepository.findByTriggerTimeBetween(startTime, endTime);
    }

    /**
     * Get active alerts.
     *
     * @return List of active alerts
     */
    @Transactional(readOnly = true)
    public List<Alert> getActiveAlerts() {
        return alertRepository.findActiveAlerts();
    }

    /**
     * Get active alerts by severity.
     *
     * @param severity The severity of the alert
     * @return List of active alerts with the given severity
     */
    @Transactional(readOnly = true)
    public List<Alert> getActiveAlertsBySeverity(String severity) {
        return alertRepository.findActiveAlertsBySeverity(severity);
    }

    /**
     * Count alerts by severity within a time range.
     *
     * @param severity The severity of the alert
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of alerts with the given severity within the time range
     */
    @Transactional(readOnly = true)
    public Long countAlertsBySeverity(String severity, Instant startTime, Instant endTime) {
        return alertRepository.countBySeverityAndTimeRange(severity, startTime, endTime);
    }

    /**
     * Calculate the average time to resolve alerts by severity.
     *
     * @param severity The severity of the alert
     * @return The average time to resolve alerts in seconds
     */
    @Transactional(readOnly = true)
    public Double calculateAverageTimeToResolve(String severity) {
        return alertRepository.calculateAverageTimeToResolveBySeverity(severity);
    }
}
