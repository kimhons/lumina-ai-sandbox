package ai.lumina.collaboration.model;

import java.time.LocalDateTime;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.JoinColumn;
import javax.persistence.ManyToOne;
import javax.persistence.Table;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/**
 * Represents access control for an agent to a shared context.
 */
@Entity
@Table(name = "context_access")
@JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
public class ContextAccess {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String agentId;
    
    private String accessLevel;
    
    private LocalDateTime grantedAt;
    
    private String grantedBy;
    
    private LocalDateTime expiresAt;
    
    @ManyToOne
    @JoinColumn(name = "context_id")
    @JsonIgnore
    private SharedContext context;

    public ContextAccess() {
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

    public String getAccessLevel() {
        return accessLevel;
    }

    public void setAccessLevel(String accessLevel) {
        this.accessLevel = accessLevel;
    }

    public LocalDateTime getGrantedAt() {
        return grantedAt;
    }

    public void setGrantedAt(LocalDateTime grantedAt) {
        this.grantedAt = grantedAt;
    }

    public String getGrantedBy() {
        return grantedBy;
    }

    public void setGrantedBy(String grantedBy) {
        this.grantedBy = grantedBy;
    }

    public LocalDateTime getExpiresAt() {
        return expiresAt;
    }

    public void setExpiresAt(LocalDateTime expiresAt) {
        this.expiresAt = expiresAt;
    }

    public SharedContext getContext() {
        return context;
    }

    public void setContext(SharedContext context) {
        this.context = context;
    }
    
    /**
     * Check if access has expired.
     * 
     * @return True if access has expired, false otherwise
     */
    public boolean isExpired() {
        return expiresAt != null && LocalDateTime.now().isAfter(expiresAt);
    }
    
    /**
     * Check if the agent can perform the specified operation.
     * 
     * @param operation The operation to check
     * @return True if the agent can perform the operation, false otherwise
     */
    public boolean canPerform(String operation) {
        if (isExpired()) {
            return false;
        }
        
        if (accessLevel.equals("ADMIN")) {
            return true;
        }
        
        if (accessLevel.equals("READ_WRITE")) {
            return !operation.equals("DELETE");
        }
        
        if (accessLevel.equals("READ_ONLY")) {
            return operation.equals("READ") || operation.equals("SUBSCRIBE");
        }
        
        return false;
    }

    @Override
    public String toString() {
        return "ContextAccess{" +
                "id=" + id +
                ", agentId='" + agentId + '\'' +
                ", accessLevel='" + accessLevel + '\'' +
                ", grantedAt=" + grantedAt +
                ", expiresAt=" + expiresAt +
                '}';
    }
}
