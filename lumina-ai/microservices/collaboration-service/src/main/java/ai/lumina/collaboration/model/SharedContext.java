package ai.lumina.collaboration.model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import javax.persistence.CascadeType;
import javax.persistence.CollectionTable;
import javax.persistence.Column;
import javax.persistence.ElementCollection;
import javax.persistence.Entity;
import javax.persistence.FetchType;
import javax.persistence.Id;
import javax.persistence.JoinColumn;
import javax.persistence.OneToMany;
import javax.persistence.Table;

import org.hibernate.annotations.Type;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/**
 * Represents a shared context between multiple agents.
 */
@Entity
@Table(name = "shared_contexts")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class SharedContext {

    @Id
    private String id;
    
    private String name;
    
    private String contextType;
    
    private String ownerId;
    
    private LocalDateTime createdAt;
    
    private LocalDateTime updatedAt;
    
    @Type(type = "json")
    @Column(columnDefinition = "json")
    private Map<String, Object> content = new HashMap<>();
    
    @OneToMany(mappedBy = "context", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<ContextAccess> accessControl = new ArrayList<>();
    
    private String currentVersionId;
    
    @Type(type = "json")
    @Column(columnDefinition = "json")
    private Map<String, Object> metadata = new HashMap<>();
    
    @ElementCollection(fetch = FetchType.LAZY)
    @CollectionTable(name = "context_subscribers", joinColumns = @JoinColumn(name = "context_id"))
    @Column(name = "agent_id")
    private Set<String> subscribers = new HashSet<>();

    public SharedContext() {
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getContextType() {
        return contextType;
    }

    public void setContextType(String contextType) {
        this.contextType = contextType;
    }

    public String getOwnerId() {
        return ownerId;
    }

    public void setOwnerId(String ownerId) {
        this.ownerId = ownerId;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    public Map<String, Object> getContent() {
        return content;
    }

    public void setContent(Map<String, Object> content) {
        this.content = content;
    }

    public List<ContextAccess> getAccessControl() {
        return accessControl;
    }

    public void setAccessControl(List<ContextAccess> accessControl) {
        this.accessControl = accessControl;
    }

    public String getCurrentVersionId() {
        return currentVersionId;
    }

    public void setCurrentVersionId(String currentVersionId) {
        this.currentVersionId = currentVersionId;
    }

    public Map<String, Object> getMetadata() {
        return metadata;
    }

    public void setMetadata(Map<String, Object> metadata) {
        this.metadata = metadata;
    }

    public Set<String> getSubscribers() {
        return subscribers;
    }

    public void setSubscribers(Set<String> subscribers) {
        this.subscribers = subscribers;
    }

    @Override
    public String toString() {
        return "SharedContext{" +
                "id='" + id + '\'' +
                ", name='" + name + '\'' +
                ", contextType='" + contextType + '\'' +
                ", ownerId='" + ownerId + '\'' +
                ", createdAt=" + createdAt +
                ", updatedAt=" + updatedAt +
                ", currentVersionId='" + currentVersionId + '\'' +
                ", subscribers=" + subscribers.size() +
                '}';
    }
}
