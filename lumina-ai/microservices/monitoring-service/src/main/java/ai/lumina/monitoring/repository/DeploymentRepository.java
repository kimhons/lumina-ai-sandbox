package ai.lumina.monitoring.repository;

import ai.lumina.monitoring.model.Deployment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;

/**
 * Repository for managing Deployment entities.
 */
@Repository
public interface DeploymentRepository extends JpaRepository<Deployment, String> {

    /**
     * Find deployments by service name.
     *
     * @param serviceName The name of the service
     * @return List of deployments for the given service
     */
    List<Deployment> findByServiceName(String serviceName);

    /**
     * Find deployments by version.
     *
     * @param version The version of the deployment
     * @return List of deployments with the given version
     */
    List<Deployment> findByVersion(String version);

    /**
     * Find deployments by environment.
     *
     * @param environment The environment of the deployment
     * @return List of deployments for the given environment
     */
    List<Deployment> findByEnvironment(String environment);

    /**
     * Find deployments by status.
     *
     * @param status The status of the deployment
     * @return List of deployments with the given status
     */
    List<Deployment> findByStatus(String status);

    /**
     * Find deployments by service name and environment.
     *
     * @param serviceName The name of the service
     * @param environment The environment of the deployment
     * @return List of deployments for the given service and environment
     */
    List<Deployment> findByServiceNameAndEnvironment(String serviceName, String environment);

    /**
     * Find deployments within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of deployments within the time range
     */
    List<Deployment> findByTimestampBetween(Instant startTime, Instant endTime);

    /**
     * Find the most recent deployment for a service in an environment.
     *
     * @param serviceName The name of the service
     * @param environment The environment of the deployment
     * @return The most recent deployment for the service in the environment
     */
    Deployment findFirstByServiceNameAndEnvironmentOrderByTimestampDesc(String serviceName, String environment);

    /**
     * Find deployments by deployment strategy.
     *
     * @param deploymentStrategy The deployment strategy
     * @return List of deployments with the given deployment strategy
     */
    List<Deployment> findByDeploymentStrategy(String deploymentStrategy);

    /**
     * Count deployments by status within a time range.
     *
     * @param status The status of the deployment
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of deployments with the given status within the time range
     */
    @Query("SELECT COUNT(d) FROM Deployment d WHERE d.status = :status AND d.timestamp BETWEEN :startTime AND :endTime")
    Long countByStatusAndTimeRange(@Param("status") String status, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);

    /**
     * Calculate the average deployment duration by environment.
     *
     * @param environment The environment of the deployment
     * @return The average deployment duration in milliseconds
     */
    @Query("SELECT AVG(FUNCTION('TIMESTAMPDIFF', SECOND, d.startTime, d.endTime)) FROM Deployment d WHERE d.environment = :environment AND d.status = 'completed' AND d.startTime IS NOT NULL AND d.endTime IS NOT NULL")
    Double calculateAverageDeploymentDurationByEnvironment(@Param("environment") String environment);

    /**
     * Calculate the deployment success rate by environment within a time range.
     *
     * @param environment The environment of the deployment
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The deployment success rate (percentage)
     */
    @Query("SELECT (COUNT(CASE WHEN d.status = 'completed' THEN 1 ELSE NULL END) * 100.0 / COUNT(*)) FROM Deployment d WHERE d.environment = :environment AND d.timestamp BETWEEN :startTime AND :endTime")
    Double calculateDeploymentSuccessRateByEnvironmentAndTimeRange(@Param("environment") String environment, @Param("startTime") Instant startTime, @Param("endTime") Instant endTime);
}
