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
 * Represents a user identity in the system.
 * Manages user identity information, credentials, and authentication methods.
 */
@Entity
@Table(name = "user_identities")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserIdentity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String username;

    @Column(nullable = false)
    private String passwordHash;

    @Column(nullable = false)
    private String salt;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = true)
    private String fullName;

    @ElementCollection
    @CollectionTable(name = "user_roles", joinColumns = @JoinColumn(name = "user_id"))
    @Column(name = "role")
    private Set<String> roles = new HashSet<>();

    @ElementCollection
    @CollectionTable(name = "user_attributes", joinColumns = @JoinColumn(name = "user_id"))
    @MapKeyColumn(name = "attribute_key")
    @Column(name = "attribute_value")
    private Set<String> attributes = new HashSet<>();

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private MfaType mfaType;

    @Column(nullable = true)
    private String mfaSecret;

    @Column(nullable = false)
    private Boolean accountLocked;

    @Column(nullable = false)
    private Boolean accountExpired;

    @Column(nullable = false)
    private Boolean credentialsExpired;

    @Column(nullable = false)
    private Boolean enabled;

    @Column(nullable = true)
    private LocalDateTime lastLoginAt;

    @Column(nullable = true)
    private LocalDateTime passwordChangedAt;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime updatedAt;

    /**
     * Enum representing the type of multi-factor authentication.
     */
    public enum MfaType {
        NONE,
        TOTP,
        SMS,
        EMAIL,
        HARDWARE_TOKEN
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
