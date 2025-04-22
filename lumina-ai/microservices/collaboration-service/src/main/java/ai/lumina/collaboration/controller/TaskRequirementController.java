package ai.lumina.collaboration.controller;

import ai.lumina.collaboration.model.TaskRequirement;
import ai.lumina.collaboration.service.TaskRequirementService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * REST controller for managing task requirements in the collaboration system.
 */
@RestController
@RequestMapping("/api/v1/collaboration/tasks")
@RequiredArgsConstructor
@Slf4j
public class TaskRequirementController {

    private final TaskRequirementService taskRequirementService;

    /**
     * Create a new task.
     *
     * @param request the task creation request
     * @return the created task requirement
     */
    @PostMapping
    public ResponseEntity<TaskRequirement> createTask(@RequestBody TaskCreationRequest request) {
        log.info("Received request to create task: {}", request.getTaskId());
        
        try {
            TaskRequirement task = taskRequirementService.createTask(
                    request.getTaskId(),
                    request.getName(),
                    request.getDescription(),
                    request.getRequiredCapabilities(),
                    request.getDomainSpecializations(),
                    request.getPriority(),
                    request.getEstimatedDuration(),
                    request.getComplexity(),
                    request.getMinTeamSize(),
                    request.getMaxTeamSize(),
                    request.getCreatorId()
            );
            
            return ResponseEntity.status(HttpStatus.CREATED).body(task);
        } catch (IllegalArgumentException e) {
            log.warn("Failed to create task: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.CONFLICT).build();
        }
    }

    /**
     * Get a task by ID.
     *
     * @param taskId the task ID
     * @return the task requirement, or 404 if not found
     */
    @GetMapping("/{taskId}")
    public ResponseEntity<TaskRequirement> getTask(@PathVariable String taskId) {
        log.info("Received request to get task: {}", taskId);
        
        return taskRequirementService.getTask(taskId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get tasks by status.
     *
     * @param status the task status
     * @return list of task requirements
     */
    @GetMapping
    public ResponseEntity<List<TaskRequirement>> getTasksByStatus(
            @RequestParam(required = false) TaskRequirement.TaskStatus status) {
        
        log.info("Received request to get tasks by status: {}", status);
        
        List<TaskRequirement> tasks;
        if (status != null) {
            tasks = taskRequirementService.getTasksByStatus(status);
        } else {
            // If no status is provided, return all tasks
            tasks = new ArrayList<>();
            for (TaskRequirement.TaskStatus s : TaskRequirement.TaskStatus.values()) {
                tasks.addAll(taskRequirementService.getTasksByStatus(s));
            }
        }
        
        return ResponseEntity.ok(tasks);
    }

    /**
     * Update a task's status.
     *
     * @param taskId the task ID
     * @param status the new status
     * @return the updated task requirement, or 404 if not found
     */
    @PutMapping("/{taskId}/status")
    public ResponseEntity<TaskRequirement> updateTaskStatus(
            @PathVariable String taskId,
            @RequestBody StatusUpdateRequest status) {
        
        log.info("Received request to update status for task: {} to {}", taskId, status.getStatus());
        
        return taskRequirementService.updateTaskStatus(taskId, status.getStatus())
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Update a task's required capabilities.
     *
     * @param taskId the task ID
     * @param capabilities the new required capabilities map
     * @return the updated task requirement, or 404 if not found
     */
    @PutMapping("/{taskId}/capabilities")
    public ResponseEntity<TaskRequirement> updateRequiredCapabilities(
            @PathVariable String taskId,
            @RequestBody Map<String, Float> capabilities) {
        
        log.info("Received request to update required capabilities for task: {}", taskId);
        
        return taskRequirementService.updateRequiredCapabilities(taskId, capabilities)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Update a task's domain specializations.
     *
     * @param taskId the task ID
     * @param specializations the new domain specializations set
     * @return the updated task requirement, or 404 if not found
     */
    @PutMapping("/{taskId}/specializations")
    public ResponseEntity<TaskRequirement> updateDomainSpecializations(
            @PathVariable String taskId,
            @RequestBody Set<String> specializations) {
        
        log.info("Received request to update domain specializations for task: {}", taskId);
        
        return taskRequirementService.updateDomainSpecializations(taskId, specializations)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Cancel a task.
     *
     * @param taskId the task ID
     * @return 204 if successful, 404 if task not found
     */
    @DeleteMapping("/{taskId}")
    public ResponseEntity<Void> cancelTask(@PathVariable String taskId) {
        log.info("Received request to cancel task: {}", taskId);
        
        boolean success = taskRequirementService.cancelTask(taskId);
        return success ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }

    /**
     * Find tasks by required capability.
     *
     * @param capability the capability name
     * @param minLevel optional minimum capability level
     * @return list of matching task requirements
     */
    @GetMapping("/search/by-capability")
    public ResponseEntity<List<TaskRequirement>> findTasksByRequiredCapability(
            @RequestParam String capability,
            @RequestParam(required = false) Float minLevel) {
        
        log.info("Received request to find tasks by required capability: {}, minLevel: {}", capability, minLevel);
        
        List<TaskRequirement> tasks = taskRequirementService.findTasksByRequiredCapability(capability, minLevel);
        return ResponseEntity.ok(tasks);
    }

    /**
     * Find tasks by domain specialization.
     *
     * @param specialization the domain specialization
     * @return list of matching task requirements
     */
    @GetMapping("/search/by-specialization")
    public ResponseEntity<List<TaskRequirement>> findTasksByDomainSpecialization(
            @RequestParam String specialization) {
        
        log.info("Received request to find tasks by domain specialization: {}", specialization);
        
        List<TaskRequirement> tasks = taskRequirementService.findTasksByDomainSpecialization(specialization);
        return ResponseEntity.ok(tasks);
    }

    /**
     * Find tasks by minimum priority.
     *
     * @param minPriority the minimum priority
     * @return list of matching task requirements
     */
    @GetMapping("/search/by-priority")
    public ResponseEntity<List<TaskRequirement>> findTasksByMinPriority(
            @RequestParam int minPriority) {
        
        log.info("Received request to find tasks by minimum priority: {}", minPriority);
        
        List<TaskRequirement> tasks = taskRequirementService.findTasksByMinPriority(minPriority);
        return ResponseEntity.ok(tasks);
    }

    /**
     * Find tasks by creator.
     *
     * @param creatorId the creator ID
     * @return list of matching task requirements
     */
    @GetMapping("/search/by-creator")
    public ResponseEntity<List<TaskRequirement>> findTasksByCreator(
            @RequestParam String creatorId) {
        
        log.info("Received request to find tasks by creator: {}", creatorId);
        
        List<TaskRequirement> tasks = taskRequirementService.findTasksByCreator(creatorId);
        return ResponseEntity.ok(tasks);
    }

    /**
     * Task creation request.
     */
    public static class TaskCreationRequest {
        private String taskId;
        private String name;
        private String description;
        private Map<String, Float> requiredCapabilities;
        private Set<String> domainSpecializations;
        private int priority;
        private float estimatedDuration;
        private int complexity;
        private int minTeamSize;
        private int maxTeamSize;
        private String creatorId;

        // Getters and setters
        public String getTaskId() { return taskId; }
        public void setTaskId(String taskId) { this.taskId = taskId; }
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        
        public Map<String, Float> getRequiredCapabilities() { return requiredCapabilities; }
        public void setRequiredCapabilities(Map<String, Float> requiredCapabilities) { this.requiredCapabilities = requiredCapabilities; }
        
        public Set<String> getDomainSpecializations() { return domainSpecializations; }
        public void setDomainSpecializations(Set<String> domainSpecializations) { this.domainSpecializations = domainSpecializations; }
        
        public int getPriority() { return priority; }
        public void setPriority(int priority) { this.priority = priority; }
        
        public float getEstimatedDuration() { return estimatedDuration; }
        public void setEstimatedDuration(float estimatedDuration) { this.estimatedDuration = estimatedDuration; }
        
        public int getComplexity() { return complexity; }
        public void setComplexity(int complexity) { this.complexity = complexity; }
        
        public int getMinTeamSize() { return minTeamSize; }
        public void setMinTeamSize(int minTeamSize) { this.minTeamSize = minTeamSize; }
        
        public int getMaxTeamSize() { return maxTeamSize; }
        public void setMaxTeamSize(int maxTeamSize) { this.maxTeamSize = maxTeamSize; }
        
        public String getCreatorId() { return creatorId; }
        public void setCreatorId(String creatorId) { this.creatorId = creatorId; }
    }

    /**
     * Status update request.
     */
    public static class StatusUpdateRequest {
        private TaskRequirement.TaskStatus status;

        // Getters and setters
        public TaskRequirement.TaskStatus getStatus() { return status; }
        public void setStatus(TaskRequirement.TaskStatus status) { this.status = status; }
    }
}
