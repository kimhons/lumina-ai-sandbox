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
 * Represents a compliance requirement in the system.
 * Defines regulatory requirements and associated checks for compliance reporting.
 */
@Entity
@Table(name = "compliance_requirements")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ComplianceRequirement {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String requirementId;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, length = 2000)
    private String description;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private FrameworkType frameworkType;

    @Column(nullable = false)
    private String frameworkVersion;

    @Column(nullable = false)
    private String category;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private RequirementSeverity severity;

    @ElementCollection
    @CollectionTable(name = "compliance_checks", joinColumns = @JoinColumn(name = "requirement_id"))
    @Column(name = "check_description")
    private Set<String> complianceChecks = new HashSet<>();

    @ElementCollection
    @CollectionTable(name = "compliance_evidence_types", joinColumns = @JoinColumn(name = "requirement_id"))
    @Column(name = "evidence_type")
    private Set<String> evidenceTypes = new HashSet<>();

    @Column(nullable = false)
    private Boolean enabled;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    /**
     * Enum representing the type of compliance framework.
     */
    public enum FrameworkType {
        GDPR,
        HIPAA,
        SOC2,
        CCPA,
        PCI_DSS,
        ISO27001,
        NIST_CSF,
        CUSTOM
    }

    /**
     * Enum representing the severity of the compliance requirement.
     */
    public enum RequirementSeverity {
        CRITICAL,
        HIGH,
        MEDIUM,
        LOW
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
