package ai.lumina.security.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

/**
 * Represents an access control policy in the system.
 * Policies define rules for resource access based on roles, attributes, and contexts.
 */
@Entity
@Table(name = "access_control_policies")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AccessControlPolicy {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name;

    @Column(nullable = false)
    private String description;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private PolicyType policyType;

    @Column(nullable = false)
    private String resourcePattern;

    @Column(nullable = false)
    private String actionPattern;

    @ElementCollection
    @CollectionTable(name = "policy_role_constraints", joinColumns = @JoinColumn(name = "policy_id"))
    @Column(name = "role_constraint")
    private Set<String> roleConstraints = new HashSet<>();

    @ElementCollection
    @CollectionTable(name = "policy_attribute_constraints", joinColumns = @JoinColumn(name = "policy_id"))
    @Column(name = "attribute_constraint")
    private Set<String> attributeConstraints = new HashSet<>();

    @ElementCollection
    @CollectionTable(name = "policy_context_constraints", joinColumns = @JoinColumn(name = "policy_id"))
    @Column(name = "context_constraint")
    private Set<String> contextConstraints = new HashSet<>();

    @Column(nullable = false)
    private String effect;

    @Column(nullable = false)
    private Integer priority;

    @Column(nullable = false)
    private Boolean enabled;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    @Column(nullable = false)
    private String createdBy;

    @Column(nullable = false)
    private String updatedBy;

    /**
     * Enum representing the type of policy.
     */
    public enum PolicyType {
        RBAC,    // Role-Based Access Control
        ABAC,    // Attribute-Based Access Control
        CONTEXT, // Context-Aware Access Control
        HYBRID   // Combination of multiple policy types
    }

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
