package ai.lumina.monitoring.repository;

import ai.lumina.monitoring.model.HealthCheck;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;

/**
 * Repository for managing HealthCheck entities.
 */
@Repository
public interface HealthCheckRepository extends JpaRepository<HealthCheck, Long> {

    /**
     * Find health checks by component name.
     *
     * @param componentName The name of the component
     * @return List of health checks for the given component
     */
    List<HealthCheck> findByComponentName(String componentName);

    /**
     * Find health checks by component type.
     *
     * @param componentType The type of the component
     * @return List of health checks for the given component type
     */
    List<HealthCheck> findByComponentType(String componentType);

    /**
     * Find health checks by status.
     *
     * @param status The status of the health check
     * @return List of health checks with the given status
     */
    List<HealthCheck> findByStatus(String status);

    /**
     * Find health checks by component name and status.
     *
     * @param componentName The name of the component
     * @param status The status of the health check
     * @return List of health checks for the given component with the given status
     */
    List<HealthCheck> findByComponentNameAndStatus(String componentName, String status);

    /**
     * Find health checks within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of health checks within the time range
     */
    List<HealthCheck> findByTimestampBetween(Instant startTime, Instant endTime);

    /**
     * Find the most recent health check for a component.
     *
     * @param componentName The name of the component
     * @return The most recent health check for the component
     */
    HealthCheck findFirstByComponentNameOrderByTimestampDesc(String componentName);

    /**
     * Find the most recent health checks for all components.
     *
     * @return List of the most recent health check for each component
     */
    @Query("SELECT h FROM HealthCheck h WHERE h.timestamp = (SELECT MAX(h2.timestamp) FROM HealthCheck h2 WHERE h2.componentName = h.componentName)")
    List<HealthCheck> findMostRecentHealthChecksForAllComponents();

    /**
     * Count health checks by status within a time range.
     *
     * @param status The status of the health check
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of health checks with the given status within the time range
     */
    @Query("SELECT COUNT(h) FROM HealthCheck h WHERE h.status = :status AND h.timestamp BETWEEN :startTime AND :endTime")
    Long countByStatusAndTimeRange(@Param("status") String status, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);

    /**
     * Calculate the average response time for a component within a time range.
     *
     * @param componentName The name of the component
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average response time for the component
     */
    @Query("SELECT AVG(h.responseTimeMs) FROM HealthCheck h WHERE h.componentName = :componentName AND h.timestamp BETWEEN :startTime AND :endTime")
    Double calculateAverageResponseTimeByComponentAndTimeRange(@Param("componentName") String componentName, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);
}
