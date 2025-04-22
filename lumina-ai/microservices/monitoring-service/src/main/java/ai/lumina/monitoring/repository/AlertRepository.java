package ai.lumina.monitoring.repository;

import ai.lumina.monitoring.model.Alert;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;

/**
 * Repository for managing Alert entities.
 */
@Repository
public interface AlertRepository extends JpaRepository<Alert, Long> {

    /**
     * Find alerts by name.
     *
     * @param name The name of the alert
     * @return List of alerts with the given name
     */
    List<Alert> findByName(String name);

    /**
     * Find alerts by severity.
     *
     * @param severity The severity of the alert
     * @return List of alerts with the given severity
     */
    List<Alert> findBySeverity(String severity);

    /**
     * Find alerts by status.
     *
     * @param status The status of the alert
     * @return List of alerts with the given status
     */
    List<Alert> findByStatus(String status);

    /**
     * Find alerts by source.
     *
     * @param source The source of the alert
     * @return List of alerts from the given source
     */
    List<Alert> findBySource(String source);

    /**
     * Find alerts by severity and status.
     *
     * @param severity The severity of the alert
     * @param status The status of the alert
     * @return List of alerts with the given severity and status
     */
    List<Alert> findBySeverityAndStatus(String severity, String status);

    /**
     * Find alerts within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of alerts within the time range
     */
    List<Alert> findByTriggerTimeBetween(Instant startTime, Instant endTime);

    /**
     * Find active alerts (not resolved).
     *
     * @return List of active alerts
     */
    @Query("SELECT a FROM Alert a WHERE a.resolveTime IS NULL")
    List<Alert> findActiveAlerts();

    /**
     * Find active alerts by severity.
     *
     * @param severity The severity of the alert
     * @return List of active alerts with the given severity
     */
    @Query("SELECT a FROM Alert a WHERE a.resolveTime IS NULL AND a.severity = :severity")
    List<Alert> findActiveAlertsBySeverity(@Param("severity") String severity);

    /**
     * Find active alerts by source.
     *
     * @param source The source of the alert
     * @return List of active alerts from the given source
     */
    @Query("SELECT a FROM Alert a WHERE a.resolveTime IS NULL AND a.source = :source")
    List<Alert> findActiveAlertsBySource(@Param("source") String source);

    /**
     * Count alerts by severity within a time range.
     *
     * @param severity The severity of the alert
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of alerts with the given severity within the time range
     */
    @Query("SELECT COUNT(a) FROM Alert a WHERE a.severity = :severity AND a.triggerTime BETWEEN :startTime AND :endTime")
    Long countBySeverityAndTimeRange(@Param("severity") String severity, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);

    /**
     * Calculate the average time to resolve alerts by severity.
     *
     * @param severity The severity of the alert
     * @return The average time to resolve alerts in milliseconds
     */
    @Query("SELECT AVG(FUNCTION('TIMESTAMPDIFF', SECOND, a.triggerTime, a.resolveTime)) FROM Alert a WHERE a.severity = :severity AND a.resolveTime IS NOT NULL")
    Double calculateAverageTimeToResolveBySeverity(@Param("severity") String severity);
}
