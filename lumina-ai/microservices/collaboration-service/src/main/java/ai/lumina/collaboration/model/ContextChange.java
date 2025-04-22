package ai.lumina.collaboration.model;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.JoinColumn;
import javax.persistence.ManyToOne;
import javax.persistence.Table;

import org.hibernate.annotations.Type;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/**
 * Represents a change to a shared context.
 */
@Entity
@Table(name = "context_changes")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class ContextChange {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String agentId;
    
    private LocalDateTime timestamp;
    
    private String operation;
    
    private String path;
    
    @Type(type = "json")
    @Column(columnDefinition = "json")
    private Object oldValue;
    
    @Type(type = "json")
    @Column(columnDefinition = "json")
    private Object newValue;
    
    @Type(type = "json")
    @Column(columnDefinition = "json")
    private Map<String, Object> metadata = new HashMap<>();
    
    @ManyToOne
    @JoinColumn(name = "version_id")
    @JsonIgnore
    private ContextVersion version;

    public ContextChange() {
    }

    public ContextChange(String agentId, LocalDateTime timestamp, String operation, String path, 
                        Object oldValue, Object newValue, Map<String, Object> metadata) {
        this.agentId = agentId;
        this.timestamp = timestamp;
        this.operation = operation;
        this.path = path;
        this.oldValue = oldValue;
        this.newValue = newValue;
        this.metadata = metadata != null ? metadata : new HashMap<>();
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getAgentId() {
        return agentId;
    }

    public void setAgentId(String agentId) {
        this.agentId = agentId;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public String getOperation() {
        return operation;
    }

    public void setOperation(String operation) {
        this.operation = operation;
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }

    public Object getOldValue() {
        return oldValue;
    }

    public void setOldValue(Object oldValue) {
        this.oldValue = oldValue;
    }

    public Object getNewValue() {
        return newValue;
    }

    public void setNewValue(Object newValue) {
        this.newValue = newValue;
    }

    public Map<String, Object> getMetadata() {
        return metadata;
    }

    public void setMetadata(Map<String, Object> metadata) {
        this.metadata = metadata;
    }

    public ContextVersion getVersion() {
        return version;
    }

    public void setVersion(ContextVersion version) {
        this.version = version;
    }

    @Override
    public String toString() {
        return "ContextChange{" +
                "id=" + id +
                ", agentId='" + agentId + '\'' +
                ", operation='" + operation + '\'' +
                ", path='" + path + '\'' +
                '}';
    }
}
