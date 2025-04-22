package ai.lumina.monitoring.controller;

import ai.lumina.monitoring.model.Alert;
import ai.lumina.monitoring.service.AlertService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * REST controller for managing alerts in the monitoring system.
 */
@RestController
@RequestMapping("/api/alerts")
@RequiredArgsConstructor
public class AlertController {

    private final AlertService alertService;

    /**
     * Create a new alert.
     *
     * @param request The alert request
     * @return The created alert
     */
    @PostMapping
    public ResponseEntity<Alert> createAlert(@RequestBody AlertCreateRequest request) {
        Alert alert = alertService.createAlert(
                request.getName(),
                request.getSeverity(),
                request.getSource(),
                request.getDescription(),
                request.getRule(),
                request.getTriggerValue(),
                request.getThresholdValue(),
                request.getLabels()
        );
        return ResponseEntity.ok(alert);
    }

    /**
     * Acknowledge an alert.
     *
     * @param alertId The ID of the alert
     * @return The updated alert
     */
    @PostMapping("/{alertId}/acknowledge")
    public ResponseEntity<Alert> acknowledgeAlert(@PathVariable Long alertId) {
        Alert alert = alertService.acknowledgeAlert(alertId);
        return ResponseEntity.ok(alert);
    }

    /**
     * Resolve an alert.
     *
     * @param alertId The ID of the alert
     * @return The updated alert
     */
    @PostMapping("/{alertId}/resolve")
    public ResponseEntity<Alert> resolveAlert(@PathVariable Long alertId) {
        Alert alert = alertService.resolveAlert(alertId);
        return ResponseEntity.ok(alert);
    }

    /**
     * Get an alert by ID.
     *
     * @param alertId The ID of the alert
     * @return The alert
     */
    @GetMapping("/{alertId}")
    public ResponseEntity<Alert> getAlertById(@PathVariable Long alertId) {
        return ResponseEntity.ok(alertService.getAlertById(alertId));
    }

    /**
     * Get alerts by name.
     *
     * @param name The name of the alert
     * @return List of alerts with the given name
     */
    @GetMapping("/name/{name}")
    public ResponseEntity<List<Alert>> getAlertsByName(@PathVariable String name) {
        return ResponseEntity.ok(alertService.getAlertsByName(name));
    }

    /**
     * Get alerts by severity.
     *
     * @param severity The severity of the alert
     * @return List of alerts with the given severity
     */
    @GetMapping("/severity/{severity}")
    public ResponseEntity<List<Alert>> getAlertsBySeverity(@PathVariable String severity) {
        return ResponseEntity.ok(alertService.getAlertsBySeverity(severity));
    }

    /**
     * Get alerts by status.
     *
     * @param status The status of the alert
     * @return List of alerts with the given status
     */
    @GetMapping("/status/{status}")
    public ResponseEntity<List<Alert>> getAlertsByStatus(@PathVariable String status) {
        return ResponseEntity.ok(alertService.getAlertsByStatus(status));
    }

    /**
     * Get alerts by source.
     *
     * @param source The source of the alert
     * @return List of alerts from the given source
     */
    @GetMapping("/source/{source}")
    public ResponseEntity<List<Alert>> getAlertsBySource(@PathVariable String source) {
        return ResponseEntity.ok(alertService.getAlertsBySource(source));
    }

    /**
     * Get alerts within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of alerts within the time range
     */
    @GetMapping("/timerange")
    public ResponseEntity<List<Alert>> getAlertsInTimeRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(alertService.getAlertsInTimeRange(startTime, endTime));
    }

    /**
     * Get active alerts.
     *
     * @return List of active alerts
     */
    @GetMapping("/active")
    public ResponseEntity<List<Alert>> getActiveAlerts() {
        return ResponseEntity.ok(alertService.getActiveAlerts());
    }

    /**
     * Get active alerts by severity.
     *
     * @param severity The severity of the alert
     * @return List of active alerts with the given severity
     */
    @GetMapping("/active/severity/{severity}")
    public ResponseEntity<List<Alert>> getActiveAlertsBySeverity(@PathVariable String severity) {
        return ResponseEntity.ok(alertService.getActiveAlertsBySeverity(severity));
    }

    /**
     * Count alerts by severity within a time range.
     *
     * @param severity The severity of the alert
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of alerts with the given severity within the time range
     */
    @GetMapping("/severity/{severity}/count")
    public ResponseEntity<Long> countAlertsBySeverity(
            @PathVariable String severity,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant startTime,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) Instant endTime) {
        return ResponseEntity.ok(alertService.countAlertsBySeverity(severity, startTime, endTime));
    }

    /**
     * Calculate the average time to resolve alerts by severity.
     *
     * @param severity The severity of the alert
     * @return The average time to resolve alerts in seconds
     */
    @GetMapping("/severity/{severity}/average-resolution-time")
    public ResponseEntity<Double> calculateAverageTimeToResolve(@PathVariable String severity) {
        return ResponseEntity.ok(alertService.calculateAverageTimeToResolve(severity));
    }

    /**
     * Request object for creating an alert.
     */
    public static class AlertCreateRequest {
        private String name;
        private String severity;
        private String source;
        private String description;
        private String rule;
        private Double triggerValue;
        private Double thresholdValue;
        private Map<String, String> labels;

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getSeverity() {
            return severity;
        }

        public void setSeverity(String severity) {
            this.severity = severity;
        }

        public String getSource() {
            return source;
        }

        public void setSource(String source) {
            this.source = source;
        }

        public String getDescription() {
            return description;
        }

        public void setDescription(String description) {
            this.description = description;
        }

        public String getRule() {
            return rule;
        }

        public void setRule(String rule) {
            this.rule = rule;
        }

        public Double getTriggerValue() {
            return triggerValue;
        }

        public void setTriggerValue(Double triggerValue) {
            this.triggerValue = triggerValue;
        }

        public Double getThresholdValue() {
            return thresholdValue;
        }

        public void setThresholdValue(Double thresholdValue) {
            this.thresholdValue = thresholdValue;
        }

        public Map<String, String> getLabels() {
            return labels;
        }

        public void setLabels(Map<String, String> labels) {
            this.labels = labels;
        }
    }
}
