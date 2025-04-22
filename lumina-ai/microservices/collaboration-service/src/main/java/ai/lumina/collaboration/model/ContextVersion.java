package ai.lumina.collaboration.model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.persistence.CascadeType;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.FetchType;
import javax.persistence.Id;
import javax.persistence.OneToMany;
import javax.persistence.Table;

import org.hibernate.annotations.Type;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/**
 * Represents a version of a shared context.
 */
@Entity
@Table(name = "context_versions")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class ContextVersion {

    @Id
    private String versionId;
    
    private LocalDateTime timestamp;
    
    private String agentId;
    
    private String parentVersionId;
    
    @OneToMany(cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<ContextChange> changes = new ArrayList<>();
    
    @Type(type = "json")
    @Column(columnDefinition = "json")
    private Map<String, Object> metadata = new HashMap<>();
    
    private String hashValue;

    public ContextVersion() {
    }

    public String getVersionId() {
        return versionId;
    }

    public void setVersionId(String versionId) {
        this.versionId = versionId;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public String getAgentId() {
        return agentId;
    }

    public void setAgentId(String agentId) {
        this.agentId = agentId;
    }

    public String getParentVersionId() {
        return parentVersionId;
    }

    public void setParentVersionId(String parentVersionId) {
        this.parentVersionId = parentVersionId;
    }

    public List<ContextChange> getChanges() {
        return changes;
    }

    public void setChanges(List<ContextChange> changes) {
        this.changes = changes;
    }

    public Map<String, Object> getMetadata() {
        return metadata;
    }

    public void setMetadata(Map<String, Object> metadata) {
        this.metadata = metadata;
    }

    public String getHashValue() {
        return hashValue;
    }

    public void setHashValue(String hashValue) {
        this.hashValue = hashValue;
    }
    
    /**
     * Compute a hash value for this version.
     */
    public void computeHash() {
        StringBuilder content = new StringBuilder();
        content.append(versionId).append(":")
               .append(timestamp).append(":")
               .append(agentId).append(":")
               .append(parentVersionId);
        
        for (ContextChange change : changes) {
            content.append(":")
                   .append(change.getOperation()).append(":")
                   .append(change.getPath()).append(":")
                   .append(change.getNewValue());
        }
        
        this.hashValue = content.toString().hashCode() + "";
    }

    @Override
    public String toString() {
        return "ContextVersion{" +
                "versionId='" + versionId + '\'' +
                ", timestamp=" + timestamp +
                ", agentId='" + agentId + '\'' +
                ", changes=" + changes.size() +
                '}';
    }
}
