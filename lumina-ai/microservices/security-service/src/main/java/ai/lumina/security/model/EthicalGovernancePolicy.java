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
 * Represents an ethical governance policy in the system.
 * Defines rules for ethical AI behavior and decision-making.
 */
@Entity
@Table(name = "ethical_governance_policies")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EthicalGovernancePolicy {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String policyId;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, length = 2000)
    private String description;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private EthicalPrinciple principle;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private ApplicationDomain domain;

    @ElementCollection
    @CollectionTable(name = "ethical_fairness_rules", joinColumns = @JoinColumn(name = "policy_id"))
    @Column(name = "fairness_rule")
    private Set<String> fairnessRules = new HashSet<>();

    @ElementCollection
    @CollectionTable(name = "ethical_explainability_rules", joinColumns = @JoinColumn(name = "policy_id"))
    @Column(name = "explainability_rule")
    private Set<String> explainabilityRules = new HashSet<>();

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private HumanOversightLevel humanOversightLevel;

    @Column(nullable = false)
    private Boolean enabled;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    /**
     * Enum representing ethical principles.
     */
    public enum EthicalPrinciple {
        FAIRNESS,
        TRANSPARENCY,
        EXPLAINABILITY,
        HUMAN_AUTONOMY,
        PRIVACY,
        ACCOUNTABILITY,
        SAFETY,
        INCLUSIVITY
    }

    /**
     * Enum representing application domains.
     */
    public enum ApplicationDomain {
        HEALTHCARE,
        FINANCE,
        LEGAL,
        EDUCATION,
        EMPLOYMENT,
        SOCIAL_MEDIA,
        GENERAL_PURPOSE
    }

    /**
     * Enum representing human oversight levels.
     */
    public enum HumanOversightLevel {
        HUMAN_IN_COMMAND,
        HUMAN_IN_THE_LOOP,
        HUMAN_ON_THE_LOOP,
        HUMAN_OVERSIGHT,
        FULLY_AUTONOMOUS
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
