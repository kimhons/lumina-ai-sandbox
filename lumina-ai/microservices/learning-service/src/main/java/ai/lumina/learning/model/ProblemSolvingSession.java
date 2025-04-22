package ai.lumina.learning.model;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.EnumType;
import javax.persistence.Enumerated;
import javax.persistence.Id;
import javax.persistence.Lob;
import javax.persistence.Table;

import org.hibernate.annotations.Type;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Model class representing a problem solving session.
 * This entity stores metadata about collaborative problem solving activities.
 */
@Entity
@Table(name = "problem_solving_sessions")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProblemSolvingSession {

    @Id
    private String id;
    
    private String problemId;
    
    private String teamId;
    
    private String contextId;
    
    @Enumerated(EnumType.STRING)
    private ProblemType problemType;
    
    private String domain;
    
    @Lob
    @Type(type = "org.hibernate.type.TextType")
    @Column(columnDefinition = "TEXT")
    private String problemSpecJson;
    
    private LocalDateTime startedAt;
    
    private LocalDateTime completedAt;
    
    @Enumerated(EnumType.STRING)
    private SessionStatus status;
    
    @Lob
    @Type(type = "org.hibernate.type.TextType")
    @Column(columnDefinition = "TEXT")
    private String solutionJson;
    
    @Lob
    @Type(type = "org.hibernate.type.TextType")
    @Column(columnDefinition = "TEXT")
    private String verificationResultJson;
    
    @Lob
    @Type(type = "org.hibernate.type.TextType")
    @Column(columnDefinition = "TEXT")
    private String metadataJson;
    
    /**
     * Enum representing the type of problem.
     */
    public enum ProblemType {
        CLASSIFICATION,
        REGRESSION,
        CLUSTERING,
        OPTIMIZATION,
        RECOMMENDATION,
        NATURAL_LANGUAGE,
        COMPUTER_VISION,
        CUSTOM
    }
    
    /**
     * Enum representing the status of a problem solving session.
     */
    public enum SessionStatus {
        INITIALIZED,
        ANALYZING,
        DECOMPOSING,
        TEAM_FORMATION,
        CONTEXT_CREATION,
        SOLVING,
        VERIFYING,
        COMPLETED,
        FAILED,
        ABORTED
    }
    
    /**
     * Creates a new instance with default values.
     * 
     * @return A new ProblemSolvingSession instance
     */
    public static ProblemSolvingSession createNew() {
        return ProblemSolvingSession.builder()
                .id(UUID.randomUUID().toString())
                .startedAt(LocalDateTime.now())
                .status(SessionStatus.INITIALIZED)
                .build();
    }
    
    /**
     * Gets problem specification as a Map.
     * 
     * @return Map of problem specification
     */
    public Map<String, Object> getProblemSpec() {
        // In a real implementation, this would parse the JSON string
        // For simplicity, we return an empty map
        return new HashMap<>();
    }
    
    /**
     * Sets problem specification from a Map.
     * 
     * @param problemSpec Map of problem specification
     */
    public void setProblemSpec(Map<String, Object> problemSpec) {
        // In a real implementation, this would serialize the map to JSON
        // For simplicity, we do nothing
    }
    
    /**
     * Gets solution as a Map.
     * 
     * @return Map of solution
     */
    public Map<String, Object> getSolution() {
        // In a real implementation, this would parse the JSON string
        // For simplicity, we return an empty map
        return new HashMap<>();
    }
    
    /**
     * Sets solution from a Map.
     * 
     * @param solution Map of solution
     */
    public void setSolution(Map<String, Object> solution) {
        // In a real implementation, this would serialize the map to JSON
        // For simplicity, we do nothing
    }
    
    /**
     * Gets verification result as a Map.
     * 
     * @return Map of verification result
     */
    public Map<String, Object> getVerificationResult() {
        // In a real implementation, this would parse the JSON string
        // For simplicity, we return an empty map
        return new HashMap<>();
    }
    
    /**
     * Sets verification result from a Map.
     * 
     * @param verificationResult Map of verification result
     */
    public void setVerificationResult(Map<String, Object> verificationResult) {
        // In a real implementation, this would serialize the map to JSON
        // For simplicity, we do nothing
    }
    
    /**
     * Gets metadata as a Map.
     * 
     * @return Map of metadata
     */
    public Map<String, Object> getMetadata() {
        // In a real implementation, this would parse the JSON string
        // For simplicity, we return an empty map
        return new HashMap<>();
    }
    
    /**
     * Sets metadata from a Map.
     * 
     * @param metadata Map of metadata
     */
    public void setMetadata(Map<String, Object> metadata) {
        // In a real implementation, this would serialize the map to JSON
        // For simplicity, we do nothing
    }
}
