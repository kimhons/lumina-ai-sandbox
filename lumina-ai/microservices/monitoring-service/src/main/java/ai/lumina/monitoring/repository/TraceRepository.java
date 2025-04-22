package ai.lumina.monitoring.repository;

import ai.lumina.monitoring.model.Trace;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;

/**
 * Repository for managing Trace entities.
 */
@Repository
public interface TraceRepository extends JpaRepository<Trace, String> {

    /**
     * Find traces by name.
     *
     * @param name The name of the trace
     * @return List of traces with the given name
     */
    List<Trace> findByName(String name);

    /**
     * Find traces by service name.
     *
     * @param serviceName The name of the service
     * @return List of traces from the given service
     */
    List<Trace> findByServiceName(String serviceName);

    /**
     * Find traces by status.
     *
     * @param status The status of the trace
     * @return List of traces with the given status
     */
    List<Trace> findByStatus(String status);

    /**
     * Find traces by name and service name.
     *
     * @param name The name of the trace
     * @param serviceName The name of the service
     * @return List of traces with the given name and service
     */
    List<Trace> findByNameAndServiceName(String name, String serviceName);

    /**
     * Find traces within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of traces within the time range
     */
    List<Trace> findByStartTimeBetween(Instant startTime, Instant endTime);

    /**
     * Find traces by name within a time range.
     *
     * @param name The name of the trace
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of traces with the given name within the time range
     */
    List<Trace> findByNameAndStartTimeBetween(String name, Instant startTime, Instant endTime);

    /**
     * Find traces by service name within a time range.
     *
     * @param serviceName The name of the service
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of traces from the given service within the time range
     */
    List<Trace> findByServiceNameAndStartTimeBetween(String serviceName, Instant startTime, Instant endTime);

    /**
     * Find traces with duration greater than a threshold.
     *
     * @param durationMs The duration threshold in milliseconds
     * @return List of traces with duration greater than the threshold
     */
    List<Trace> findByDurationMsGreaterThan(Long durationMs);

    /**
     * Calculate the average duration of traces by name within a time range.
     *
     * @param name The name of the trace
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average duration of the traces
     */
    @Query("SELECT AVG(t.durationMs) FROM Trace t WHERE t.name = :name AND t.startTime BETWEEN :startTime AND :endTime")
    Double calculateAverageDurationByNameAndTimeRange(@Param("name") String name, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);

    /**
     * Calculate the 95th percentile duration of traces by name within a time range.
     * Note: This is a native query that may be database-specific.
     *
     * @param name The name of the trace
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The 95th percentile duration of the traces
     */
    @Query(value = "SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) FROM traces WHERE name = :name AND start_time BETWEEN :startTime AND :endTime", nativeQuery = true)
    Double calculate95thPercentileDurationByNameAndTimeRange(@Param("name") String name, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);
}
