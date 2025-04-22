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
 * Model class representing a learning model in the system.
 * This entity stores metadata about machine learning models.
 */
@Entity
@Table(name = "learning_models")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LearningModel {

    @Id
    private String id;
    
    private String name;
    
    private String description;
    
    @Enumerated(EnumType.STRING)
    private ModelType type;
    
    private String version;
    
    @Lob
    @Type(type = "org.hibernate.type.TextType")
    @Column(columnDefinition = "TEXT")
    private String configuration;
    
    private String storageLocation;
    
    private LocalDateTime createdAt;
    
    private LocalDateTime updatedAt;
    
    private String createdBy;
    
    @Enumerated(EnumType.STRING)
    private ModelStatus status;
    
    @Lob
    @Type(type = "org.hibernate.type.TextType")
    @Column(columnDefinition = "TEXT")
    private String metadataJson;
    
    /**
     * Enum representing the type of learning model.
     */
    public enum ModelType {
        CLASSIFICATION,
        REGRESSION,
        CLUSTERING,
        REINFORCEMENT,
        GENERATIVE,
        CUSTOM
    }
    
    /**
     * Enum representing the status of a learning model.
     */
    public enum ModelStatus {
        DRAFT,
        TRAINING,
        TRAINED,
        VALIDATED,
        DEPLOYED,
        ARCHIVED,
        FAILED
    }
    
    /**
     * Creates a new instance with default values.
     * 
     * @return A new LearningModel instance
     */
    public static LearningModel createNew() {
        return LearningModel.builder()
                .id(UUID.randomUUID().toString())
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .status(ModelStatus.DRAFT)
                .build();
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
