package ai.lumina.monitoring.repository;

import ai.lumina.monitoring.model.PerformanceProfile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;

/**
 * Repository for managing PerformanceProfile entities.
 */
@Repository
public interface PerformanceProfileRepository extends JpaRepository<PerformanceProfile, Long> {

    /**
     * Find performance profiles by operation name.
     *
     * @param operationName The name of the operation
     * @return List of performance profiles for the given operation
     */
    List<PerformanceProfile> findByOperationName(String operationName);

    /**
     * Find performance profiles by service name.
     *
     * @param serviceName The name of the service
     * @return List of performance profiles for the given service
     */
    List<PerformanceProfile> findByServiceName(String serviceName);

    /**
     * Find performance profiles by operation name and service name.
     *
     * @param operationName The name of the operation
     * @param serviceName The name of the service
     * @return List of performance profiles for the given operation and service
     */
    List<PerformanceProfile> findByOperationNameAndServiceName(String operationName, String serviceName);

    /**
     * Find performance profiles within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of performance profiles within the time range
     */
    List<PerformanceProfile> findByTimestampBetween(Instant startTime, Instant endTime);

    /**
     * Find performance profiles by operation name within a time range.
     *
     * @param operationName The name of the operation
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of performance profiles for the given operation within the time range
     */
    List<PerformanceProfile> findByOperationNameAndTimestampBetween(String operationName, Instant startTime, Instant endTime);

    /**
     * Find performance profiles with duration greater than a threshold.
     *
     * @param durationMs The duration threshold in milliseconds
     * @return List of performance profiles with duration greater than the threshold
     */
    List<PerformanceProfile> findByDurationMsGreaterThan(Double durationMs);

    /**
     * Find performance profiles with errors.
     *
     * @return List of performance profiles with errors
     */
    List<PerformanceProfile> findByErrorTrue();

    /**
     * Calculate the average duration for an operation within a time range.
     *
     * @param operationName The name of the operation
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average duration for the operation
     */
    @Query("SELECT AVG(p.durationMs) FROM PerformanceProfile p WHERE p.operationName = :operationName AND p.timestamp BETWEEN :startTime AND :endTime")
    Double calculateAverageDurationByOperationAndTimeRange(@Param("operationName") String operationName, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);

    /**
     * Calculate the 95th percentile duration for an operation within a time range.
     * Note: This is a native query that may be database-specific.
     *
     * @param operationName The name of the operation
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The 95th percentile duration for the operation
     */
    @Query(value = "SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) FROM performance_profiles WHERE operation_name = :operationName AND timestamp BETWEEN :startTime AND :endTime", nativeQuery = true)
    Double calculate95thPercentileDurationByOperationAndTimeRange(@Param("operationName") String operationName, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);

    /**
     * Calculate the average CPU usage for an operation within a time range.
     *
     * @param operationName The name of the operation
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average CPU usage for the operation
     */
    @Query("SELECT AVG(p.cpuPercent) FROM PerformanceProfile p WHERE p.operationName = :operationName AND p.timestamp BETWEEN :startTime AND :endTime")
    Double calculateAverageCpuUsageByOperationAndTimeRange(@Param("operationName") String operationName, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);

    /**
     * Calculate the average memory usage for an operation within a time range.
     *
     * @param operationName The name of the operation
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average memory usage for the operation
     */
    @Query("SELECT AVG(p.memoryBytes) FROM PerformanceProfile p WHERE p.operationName = :operationName AND p.timestamp BETWEEN :startTime AND :endTime")
    Double calculateAverageMemoryUsageByOperationAndTimeRange(@Param("operationName") String operationName, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);
}
