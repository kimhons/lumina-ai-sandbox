package ai.lumina.collaboration.service;

import ai.lumina.collaboration.model.TaskRequirement;
import ai.lumina.collaboration.repository.TaskRequirementRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

/**
 * Service for managing task requirements in the collaboration system.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class TaskRequirementService {

    private final TaskRequirementRepository taskRequirementRepository;

    /**
     * Create a new task requirement.
     *
     * @param taskId the task ID
     * @param name the task name
     * @param description the task description
     * @param requiredCapabilities map of required capabilities to their minimum levels
     * @param domainSpecializations set of domain specializations
     * @param priority the task priority (1-10)
     * @param estimatedDuration the estimated duration in hours
     * @param complexity the task complexity (1-10)
     * @param minTeamSize the minimum team size
     * @param maxTeamSize the maximum team size
     * @param creatorId the creator ID
     * @return the created task requirement
     */
    @Transactional
    public TaskRequirement createTask(
            String taskId,
            String name,
            String description,
            Map<String, Float> requiredCapabilities,
            Set<String> domainSpecializations,
            int priority,
            float estimatedDuration,
            int complexity,
            int minTeamSize,
            int maxTeamSize,
            String creatorId) {
        
        log.info("Creating task: {}", taskId);
        
        // Check if task already exists
        Optional<TaskRequirement> existingTask = taskRequirementRepository.findByTaskId(taskId);
        if (existingTask.isPresent()) {
            log.warn("Task already exists: {}", taskId);
            throw new IllegalArgumentException("Task with ID " + taskId + " already exists");
        }
        
        // Create new task requirement
        TaskRequirement task = TaskRequirement.builder()
                .taskId(taskId)
                .name(name)
                .description(description)
                .requiredCapabilities(requiredCapabilities)
                .domainSpecializations(domainSpecializations)
                .priority(priority)
                .estimatedDuration(estimatedDuration)
                .complexity(complexity)
                .minTeamSize(minTeamSize)
                .maxTeamSize(maxTeamSize)
                .status(TaskRequirement.TaskStatus.CREATED)
                .creatorId(creatorId)
                .build();
        
        return taskRequirementRepository.save(task);
    }

    /**
     * Get a task requirement by ID.
     *
     * @param taskId the task ID
     * @return the task requirement, or empty if not found
     */
    @Transactional(readOnly = true)
    public Optional<TaskRequirement> getTask(String taskId) {
        return taskRequirementRepository.findByTaskId(taskId);
    }

    /**
     * Get all tasks with a specific status.
     *
     * @param status the task status
     * @return list of task requirements
     */
    @Transactional(readOnly = true)
    public List<TaskRequirement> getTasksByStatus(TaskRequirement.TaskStatus status) {
        return taskRequirementRepository.findByStatus(status);
    }

    /**
     * Update a task's status.
     *
     * @param taskId the task ID
     * @param status the new status
     * @return the updated task requirement, or empty if task not found
     */
    @Transactional
    public Optional<TaskRequirement> updateTaskStatus(String taskId, TaskRequirement.TaskStatus status) {
        Optional<TaskRequirement> taskOpt = taskRequirementRepository.findByTaskId(taskId);
        if (taskOpt.isPresent()) {
            TaskRequirement task = taskOpt.get();
            task.setStatus(status);
            return Optional.of(taskRequirementRepository.save(task));
        }
        return Optional.empty();
    }

    /**
     * Update a task's required capabilities.
     *
     * @param taskId the task ID
     * @param requiredCapabilities the new required capabilities map
     * @return the updated task requirement, or empty if task not found
     */
    @Transactional
    public Optional<TaskRequirement> updateRequiredCapabilities(String taskId, Map<String, Float> requiredCapabilities) {
        Optional<TaskRequirement> taskOpt = taskRequirementRepository.findByTaskId(taskId);
        if (taskOpt.isPresent()) {
            TaskRequirement task = taskOpt.get();
            task.setRequiredCapabilities(requiredCapabilities);
            return Optional.of(taskRequirementRepository.save(task));
        }
        return Optional.empty();
    }

    /**
     * Update a task's domain specializations.
     *
     * @param taskId the task ID
     * @param domainSpecializations the new domain specializations set
     * @return the updated task requirement, or empty if task not found
     */
    @Transactional
    public Optional<TaskRequirement> updateDomainSpecializations(String taskId, Set<String> domainSpecializations) {
        Optional<TaskRequirement> taskOpt = taskRequirementRepository.findByTaskId(taskId);
        if (taskOpt.isPresent()) {
            TaskRequirement task = taskOpt.get();
            task.setDomainSpecializations(domainSpecializations);
            return Optional.of(taskRequirementRepository.save(task));
        }
        return Optional.empty();
    }

    /**
     * Cancel a task.
     *
     * @param taskId the task ID
     * @return true if task was cancelled, false if task not found
     */
    @Transactional
    public boolean cancelTask(String taskId) {
        Optional<TaskRequirement> taskOpt = taskRequirementRepository.findByTaskId(taskId);
        if (taskOpt.isPresent()) {
            TaskRequirement task = taskOpt.get();
            task.setStatus(TaskRequirement.TaskStatus.CANCELLED);
            taskRequirementRepository.save(task);
            log.info("Cancelled task: {}", taskId);
            return true;
        }
        return false;
    }

    /**
     * Find tasks that require a specific capability.
     *
     * @param capability the capability name
     * @param minLevel the minimum capability level (optional)
     * @return list of matching task requirements
     */
    @Transactional(readOnly = true)
    public List<TaskRequirement> findTasksByRequiredCapability(String capability, Float minLevel) {
        if (minLevel != null) {
            return taskRequirementRepository.findByRequiredCapabilityWithMinLevel(capability, minLevel);
        } else {
            return taskRequirementRepository.findByRequiredCapability(capability);
        }
    }

    /**
     * Find tasks with a specific domain specialization.
     *
     * @param specialization the domain specialization
     * @return list of matching task requirements
     */
    @Transactional(readOnly = true)
    public List<TaskRequirement> findTasksByDomainSpecialization(String specialization) {
        return taskRequirementRepository.findByDomainSpecialization(specialization);
    }

    /**
     * Find tasks with a minimum priority.
     *
     * @param minPriority the minimum priority
     * @return list of matching task requirements
     */
    @Transactional(readOnly = true)
    public List<TaskRequirement> findTasksByMinPriority(int minPriority) {
        return taskRequirementRepository.findByPriorityGreaterThanEqual(minPriority);
    }

    /**
     * Find tasks created by a specific user.
     *
     * @param creatorId the creator ID
     * @return list of matching task requirements
     */
    @Transactional(readOnly = true)
    public List<TaskRequirement> findTasksByCreator(String creatorId) {
        return taskRequirementRepository.findByCreatorId(creatorId);
    }

    /**
     * Get the required capability level for a specific task and capability.
     *
     * @param taskId the task ID
     * @param capability the capability name
     * @return the required capability level, or 0.0 if not found
     */
    @Transactional(readOnly = true)
    public float getTaskRequiredCapabilityLevel(String taskId, String capability) {
        Optional<TaskRequirement> taskOpt = taskRequirementRepository.findByTaskId(taskId);
        if (taskOpt.isPresent()) {
            Map<String, Float> requiredCapabilities = taskOpt.get().getRequiredCapabilities();
            return requiredCapabilities.getOrDefault(capability, 0.0f);
        }
        return 0.0f;
    }
}
