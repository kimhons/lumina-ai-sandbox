package ai.lumina.collaboration.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Represents a workflow that orchestrates the execution of tasks by agent teams.
 */
@Entity
@Table(name = "workflows")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Workflow {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, length = 2000)
    private String description;

    @Column(nullable = false)
    private String status;  // PENDING, IN_PROGRESS, COMPLETED, FAILED

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "workflow_id")
    private List<WorkflowStep> steps = new ArrayList<>();

    @Column(nullable = false)
    private int currentStepIndex;

    @Column(nullable = true)
    private LocalDateTime startedAt;

    @Column(nullable = true)
    private LocalDateTime completedAt;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        currentStepIndex = 0;
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    /**
     * Start the workflow execution.
     * 
     * @return True if the workflow was started, false if already started or no steps
     */
    public boolean startWorkflow() {
        if (startedAt == null && !steps.isEmpty()) {
            this.startedAt = LocalDateTime.now();
            this.status = "IN_PROGRESS";
            return startCurrentStep();
        }
        return false;
    }

    /**
     * Start the current workflow step.
     * 
     * @return True if the step was started, false otherwise
     */
    public boolean startCurrentStep() {
        if (currentStepIndex < steps.size()) {
            WorkflowStep currentStep = steps.get(currentStepIndex);
            return currentStep.startStep();
        }
        return false;
    }

    /**
     * Complete the current workflow step and advance to the next.
     * 
     * @param successful Whether the step was completed successfully
     * @return True if advanced to next step, false if workflow completed or failed
     */
    public boolean completeCurrentStepAndAdvance(boolean successful) {
        if (currentStepIndex < steps.size()) {
            WorkflowStep currentStep = steps.get(currentStepIndex);
            currentStep.completeStep(successful);
            
            if (!successful) {
                this.status = "FAILED";
                this.completedAt = LocalDateTime.now();
                return false;
            }
            
            currentStepIndex++;
            
            if (currentStepIndex >= steps.size()) {
                this.status = "COMPLETED";
                this.completedAt = LocalDateTime.now();
                return false;
            }
            
            return startCurrentStep();
        }
        return false;
    }

    /**
     * Add a step to the workflow.
     * 
     * @param name The name of the step
     * @param description The description of the step
     * @param task The task associated with the step
     * @return The created workflow step
     */
    public WorkflowStep addStep(String name, String description, Task task) {
        WorkflowStep step = new WorkflowStep();
        step.setName(name);
        step.setDescription(description);
        step.setTask(task);
        step.setStepIndex(steps.size());
        step.setStatus("PENDING");
        steps.add(step);
        return step;
    }

    /**
     * Get the current step of the workflow.
     * 
     * @return The current workflow step, or null if no steps or all steps completed
     */
    @Transient
    public WorkflowStep getCurrentStep() {
        if (currentStepIndex < steps.size()) {
            return steps.get(currentStepIndex);
        }
        return null;
    }

    /**
     * Get the progress of the workflow as a percentage.
     * 
     * @return The progress percentage (0-100)
     */
    @Transient
    public double getProgressPercentage() {
        if (steps.isEmpty()) {
            return 0.0;
        }
        return (double) currentStepIndex / steps.size() * 100.0;
    }

    /**
     * Check if the workflow is active.
     * 
     * @return True if the workflow is active, false otherwise
     */
    @Transient
    public boolean isActive() {
        return status.equals("PENDING") || status.equals("IN_PROGRESS");
    }

    /**
     * Check if the workflow is successful.
     * 
     * @return True if the workflow is completed successfully, false otherwise
     */
    @Transient
    public boolean isSuccessful() {
        return status.equals("COMPLETED");
    }

    /**
     * Get the duration of the workflow in minutes.
     * 
     * @return The duration in minutes, or -1 if not started
     */
    @Transient
    public long getDurationMinutes() {
        if (startedAt == null) {
            return -1;
        }
        
        LocalDateTime endTime = completedAt != null ? completedAt : LocalDateTime.now();
        return java.time.Duration.between(startedAt, endTime).toMinutes();
    }

    /**
     * Nested entity class representing a step in the workflow.
     */
    @Entity
    @Table(name = "workflow_steps")
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class WorkflowStep {
        
        @Id
        @GeneratedValue(strategy = GenerationType.UUID)
        private String id;
        
        @Column(nullable = false)
        private String name;
        
        @Column(nullable = false, length = 1000)
        private String description;
        
        @Column(nullable = false)
        private int stepIndex;
        
        @Column(nullable = false)
        private String status;  // PENDING, IN_PROGRESS, COMPLETED, FAILED
        
        @ManyToOne
        @JoinColumn(name = "task_id")
        private Task task;
        
        @Column(nullable = true)
        private LocalDateTime startedAt;
        
        @Column(nullable = true)
        private LocalDateTime completedAt;
        
        /**
         * Start this workflow step.
         * 
         * @return True if the step was started, false if already started
         */
        public boolean startStep() {
            if (startedAt == null) {
                this.startedAt = LocalDateTime.now();
                this.status = "IN_PROGRESS";
                
                // Start the associated task if it exists
                if (task != null) {
                    task.startTask();
                }
                
                return true;
            }
            return false;
        }
        
        /**
         * Complete this workflow step.
         * 
         * @param successful Whether the step was completed successfully
         * @return True if the step was completed, false if not started or already completed
         */
        public boolean completeStep(boolean successful) {
            if (startedAt != null && completedAt == null) {
                this.completedAt = LocalDateTime.now();
                this.status = successful ? "COMPLETED" : "FAILED";
                
                // Complete the associated task if it exists
                if (task != null) {
                    task.completeTask(successful);
                }
                
                return true;
            }
            return false;
        }
        
        /**
         * Get the duration of the step in minutes.
         * 
         * @return The duration in minutes, or -1 if not started
         */
        @Transient
        public long getDurationMinutes() {
            if (startedAt == null) {
                return -1;
            }
            
            LocalDateTime endTime = completedAt != null ? completedAt : LocalDateTime.now();
            return java.time.Duration.between(startedAt, endTime).toMinutes();
        }
    }
}
