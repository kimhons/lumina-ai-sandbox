package ai.lumina.monitoring.service;

import ai.lumina.monitoring.model.Deployment;
import ai.lumina.monitoring.repository.DeploymentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Service for managing deployments in the monitoring system.
 * This service provides functionality for tracking, executing, and analyzing deployments.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class DeploymentService {

    private final DeploymentRepository deploymentRepository;

    /**
     * Prepare a deployment.
     *
     * @param serviceName The name of the service
     * @param version The version to deploy
     * @param environment The target environment
     * @param artifactPath The path to the deployment artifact
     * @param artifactChecksum The checksum of the deployment artifact
     * @param deploymentStrategy The deployment strategy
     * @param properties Additional properties for the deployment
     * @return The prepared deployment
     */
    @Transactional
    public Deployment prepareDeployment(String serviceName, String version, String environment,
                                      String artifactPath, String artifactChecksum,
                                      String deploymentStrategy, Map<String, String> properties) {
        String deploymentId = UUID.randomUUID().toString();
        Deployment deployment = Deployment.builder()
                .id(deploymentId)
                .serviceName(serviceName)
                .version(version)
                .environment(environment)
                .timestamp(Instant.now())
                .status("prepared")
                .artifactPath(artifactPath)
                .artifactChecksum(artifactChecksum)
                .deploymentStrategy(deploymentStrategy)
                .properties(properties != null ? properties : new HashMap<>())
                .build();
        
        log.info("Preparing deployment: {}", deployment);
        return deploymentRepository.save(deployment);
    }

    /**
     * Start a deployment.
     *
     * @param deploymentId The ID of the deployment
     * @return The updated deployment
     */
    @Transactional
    public Deployment startDeployment(String deploymentId) {
        Deployment deployment = deploymentRepository.findById(deploymentId)
                .orElseThrow(() -> new IllegalArgumentException("Deployment not found: " + deploymentId));
        
        if (!"prepared".equals(deployment.getStatus())) {
            throw new IllegalStateException("Deployment is not in 'prepared' state: " + deploymentId);
        }
        
        deployment.setStatus("in_progress");
        deployment.setStartTime(Instant.now());
        
        log.info("Starting deployment: {}", deployment);
        return deploymentRepository.save(deployment);
    }

    /**
     * Complete a deployment.
     *
     * @param deploymentId The ID of the deployment
     * @return The updated deployment
     */
    @Transactional
    public Deployment completeDeployment(String deploymentId) {
        Deployment deployment = deploymentRepository.findById(deploymentId)
                .orElseThrow(() -> new IllegalArgumentException("Deployment not found: " + deploymentId));
        
        if (!"in_progress".equals(deployment.getStatus())) {
            throw new IllegalStateException("Deployment is not in 'in_progress' state: " + deploymentId);
        }
        
        deployment.setStatus("completed");
        deployment.setEndTime(Instant.now());
        
        log.info("Completing deployment: {}", deployment);
        return deploymentRepository.save(deployment);
    }

    /**
     * Fail a deployment.
     *
     * @param deploymentId The ID of the deployment
     * @param error The error message
     * @return The updated deployment
     */
    @Transactional
    public Deployment failDeployment(String deploymentId, String error) {
        Deployment deployment = deploymentRepository.findById(deploymentId)
                .orElseThrow(() -> new IllegalArgumentException("Deployment not found: " + deploymentId));
        
        if (!"in_progress".equals(deployment.getStatus())) {
            throw new IllegalStateException("Deployment is not in 'in_progress' state: " + deploymentId);
        }
        
        deployment.setStatus("failed");
        deployment.setEndTime(Instant.now());
        deployment.setError(error);
        
        log.error("Deployment failed: {} - {}", deploymentId, error);
        return deploymentRepository.save(deployment);
    }

    /**
     * Get a deployment by ID.
     *
     * @param deploymentId The ID of the deployment
     * @return The deployment
     */
    @Transactional(readOnly = true)
    public Deployment getDeploymentById(String deploymentId) {
        return deploymentRepository.findById(deploymentId)
                .orElseThrow(() -> new IllegalArgumentException("Deployment not found: " + deploymentId));
    }

    /**
     * Get deployments by service name.
     *
     * @param serviceName The name of the service
     * @return List of deployments for the given service
     */
    @Transactional(readOnly = true)
    public List<Deployment> getDeploymentsByServiceName(String serviceName) {
        return deploymentRepository.findByServiceName(serviceName);
    }

    /**
     * Get deployments by environment.
     *
     * @param environment The environment of the deployment
     * @return List of deployments for the given environment
     */
    @Transactional(readOnly = true)
    public List<Deployment> getDeploymentsByEnvironment(String environment) {
        return deploymentRepository.findByEnvironment(environment);
    }

    /**
     * Get deployments by status.
     *
     * @param status The status of the deployment
     * @return List of deployments with the given status
     */
    @Transactional(readOnly = true)
    public List<Deployment> getDeploymentsByStatus(String status) {
        return deploymentRepository.findByStatus(status);
    }

    /**
     * Get deployments by service name and environment.
     *
     * @param serviceName The name of the service
     * @param environment The environment of the deployment
     * @return List of deployments for the given service and environment
     */
    @Transactional(readOnly = true)
    public List<Deployment> getDeploymentsByServiceAndEnvironment(String serviceName, String environment) {
        return deploymentRepository.findByServiceNameAndEnvironment(serviceName, environment);
    }

    /**
     * Get deployments within a time range.
     *
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return List of deployments within the time range
     */
    @Transactional(readOnly = true)
    public List<Deployment> getDeploymentsInTimeRange(Instant startTime, Instant endTime) {
        return deploymentRepository.findByTimestampBetween(startTime, endTime);
    }

    /**
     * Get the most recent deployment for a service in an environment.
     *
     * @param serviceName The name of the service
     * @param environment The environment of the deployment
     * @return The most recent deployment for the service in the environment
     */
    @Transactional(readOnly = true)
    public Deployment getMostRecentDeployment(String serviceName, String environment) {
        return deploymentRepository.findFirstByServiceNameAndEnvironmentOrderByTimestampDesc(serviceName, environment);
    }

    /**
     * Count deployments by status within a time range.
     *
     * @param status The status of the deployment
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The count of deployments with the given status within the time range
     */
    @Transactional(readOnly = true)
    public Long countDeploymentsByStatus(String status, Instant startTime, Instant endTime) {
        return deploymentRepository.countByStatusAndTimeRange(status, startTime, endTime);
    }

    /**
     * Calculate the average deployment duration by environment.
     *
     * @param environment The environment of the deployment
     * @return The average deployment duration in seconds
     */
    @Transactional(readOnly = true)
    public Double calculateAverageDeploymentDuration(String environment) {
        return deploymentRepository.calculateAverageDeploymentDurationByEnvironment(environment);
    }

    /**
     * Calculate the deployment success rate by environment within a time range.
     *
     * @param environment The environment of the deployment
     * @param startTime The start of the time range
     * @param endTime The end of the time range
     * @return The deployment success rate (percentage)
     */
    @Transactional(readOnly = true)
    public Double calculateDeploymentSuccessRate(String environment, Instant startTime, Instant endTime) {
        return deploymentRepository.calculateDeploymentSuccessRateByEnvironmentAndTimeRange(environment, startTime, endTime);
    }
}
