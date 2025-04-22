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
 * Represents a privacy policy in the system.
 * Defines privacy rules and data handling requirements.
 */
@Entity
@Table(name = "privacy_policies")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PrivacyPolicy {

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
    private DataCategory dataCategory;

    @Column(nullable = false)
    private Integer retentionPeriodDays;

    @Column(nullable = false)
    private Boolean requiresConsent;

    @Column(nullable = false)
    private Boolean allowsDataSharing;

    @ElementCollection
    @CollectionTable(name = "privacy_minimization_rules", joinColumns = @JoinColumn(name = "policy_id"))
    @Column(name = "minimization_rule")
    private Set<String> minimizationRules = new HashSet<>();

    @ElementCollection
    @CollectionTable(name = "privacy_anonymization_rules", joinColumns = @JoinColumn(name = "policy_id"))
    @Column(name = "anonymization_rule")
    private Set<String> anonymizationRules = new HashSet<>();

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private PrivacyLevel privacyLevel;

    @Column(nullable = false)
    private Boolean enabled;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    /**
     * Enum representing the category of data.
     */
    public enum DataCategory {
        PERSONAL_IDENTIFIABLE,
        SENSITIVE_PERSONAL,
        HEALTH,
        FINANCIAL,
        BEHAVIORAL,
        COMMUNICATION,
        LOCATION,
        DEVICE,
        USAGE,
        GENERAL
    }

    /**
     * Enum representing the privacy level.
     */
    public enum PrivacyLevel {
        STRICT,
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
