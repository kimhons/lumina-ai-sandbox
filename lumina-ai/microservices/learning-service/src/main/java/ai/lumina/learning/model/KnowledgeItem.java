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
 * Model class representing knowledge that can be transferred between agents.
 * This entity stores metadata about knowledge items in the system.
 */
@Entity
@Table(name = "knowledge_items")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class KnowledgeItem {

    @Id
    private String id;
    
    private String name;
    
    private String description;
    
    @Enumerated(EnumType.STRING)
    private KnowledgeType type;
    
    private String sourceAgentId;
    
    @Lob
    @Type(type = "org.hibernate.type.TextType")
    @Column(columnDefinition = "TEXT")
    private String contentJson;
    
    private LocalDateTime createdAt;
    
    private LocalDateTime updatedAt;
    
    @Enumerated(EnumType.STRING)
    private KnowledgeStatus status;
    
    @Lob
    @Type(type = "org.hibernate.type.TextType")
    @Column(columnDefinition = "TEXT")
    private String metadataJson;
    
    private Double confidenceScore;
    
    private String domainArea;
    
    /**
     * Enum representing the type of knowledge.
     */
    public enum KnowledgeType {
        MODEL,
        FEATURE,
        RULE,
        PATTERN,
        CONCEPT,
        PROCEDURE,
        FACT,
        CUSTOM
    }
    
    /**
     * Enum representing the status of a knowledge item.
     */
    public enum KnowledgeStatus {
        DRAFT,
        VALIDATED,
        SHARED,
        ARCHIVED,
        DEPRECATED
    }
    
    /**
     * Creates a new instance with default values.
     * 
     * @return A new KnowledgeItem instance
     */
    public static KnowledgeItem createNew() {
        return KnowledgeItem.builder()
                .id(UUID.randomUUID().toString())
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .status(KnowledgeStatus.DRAFT)
                .confidenceScore(1.0)
                .build();
    }
    
    /**
     * Gets content as a Map.
     * 
     * @return Map of content
     */
    public Map<String, Object> getContent() {
        // In a real implementation, this would parse the JSON string
        // For simplicity, we return an empty map
        return new HashMap<>();
    }
    
    /**
     * Sets content from a Map.
     * 
     * @param content Map of content
     */
    public void setContent(Map<String, Object> content) {
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
