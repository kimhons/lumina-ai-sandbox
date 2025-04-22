package ai.lumina.monitoring.repository;

import ai.lumina.monitoring.model.Metric;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;

/**
 * Repository for managing Metric entities.
 */
@Repository
public interface MetricRepository extends JpaRepository<Metric, Long> {

    /**
     * Find metrics by name.
     *
     * @param name The name of the metric
     * @return List of metrics with the given name
     */
    List<Metric> findByName(String name);

    /**
     * Find metrics by source.
     *
     * @param source The source of the metric
     * @return List of metrics from the given source
     */
    List<Metric> findBySource(String source);

    /**
     * Find metrics by name and source.
     *
     * @param name The name of the metric
     * @param source The source of the metric
     * @return List of metrics with the given name and source
     */
    List<Metric> findByNameAndSource(String name, String source);

    /**
     * Find metrics within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of metrics within the time range
     */
    List<Metric> findByTimestampBetween(Instant startTime, Instant endTime);

    /**
     * Find metrics by name within a time range.
     *
     * @param name The name of the metric
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of metrics with the given name within the time range
     */
    List<Metric> findByNameAndTimestampBetween(String name, Instant startTime, Instant endTime);

    /**
     * Find metrics by name and source within a time range.
     *
     * @param name The name of the metric
     * @param source The source of the metric
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of metrics with the given name and source within the time range
     */
    List<Metric> findByNameAndSourceAndTimestampBetween(String name, String source, Instant startTime, Instant endTime);

    /**
     * Calculate the average value of a metric by name within a time range.
     *
     * @param name The name of the metric
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The average value of the metric
     */
    @Query("SELECT AVG(m.value) FROM Metric m WHERE m.name = :name AND m.timestamp BETWEEN :startTime AND :endTime")
    Double calculateAverageByNameAndTimeRange(@Param("name") String name, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);

    /**
     * Calculate the maximum value of a metric by name within a time range.
     *
     * @param name The name of the metric
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The maximum value of the metric
     */
    @Query("SELECT MAX(m.value) FROM Metric m WHERE m.name = :name AND m.timestamp BETWEEN :startTime AND :endTime")
    Double calculateMaxByNameAndTimeRange(@Param("name") String name, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);

    /**
     * Calculate the minimum value of a metric by name within a time range.
     *
     * @param name The name of the metric
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The minimum value of the metric
     */
    @Query("SELECT MIN(m.value) FROM Metric m WHERE m.name = :name AND m.timestamp BETWEEN :startTime AND :endTime")
    Double calculateMinByNameAndTimeRange(@Param("name") String name, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);
}
