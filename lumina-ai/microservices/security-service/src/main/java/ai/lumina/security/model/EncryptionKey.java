package ai.lumina.security.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Represents an encryption key in the system.
 * Manages encryption keys for securing sensitive data.
 */
@Entity
@Table(name = "encryption_keys")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EncryptionKey {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String keyId;

    @Column(nullable = false)
    private String keyName;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private KeyType keyType;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private Algorithm algorithm;

    @Column(nullable = false, length = 4000)
    private String keyMaterial;

    @Column(nullable = false)
    private Integer keySize;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private KeyStatus status;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @Column(nullable = false)
    private LocalDateTime activatedAt;

    @Column(nullable = true)
    private LocalDateTime rotatedAt;

    @Column(nullable = true)
    private LocalDateTime expiresAt;

    @Column(nullable = true)
    private LocalDateTime revokedAt;

    @Column(nullable = false)
    private String createdBy;

    @Column(nullable = true)
    private String revokedBy;

    @Column(nullable = false)
    private String purpose;

    /**
     * Enum representing the type of encryption key.
     */
    public enum KeyType {
        SYMMETRIC,
        ASYMMETRIC_PRIVATE,
        ASYMMETRIC_PUBLIC,
        HMAC
    }

    /**
     * Enum representing the encryption algorithm.
     */
    public enum Algorithm {
        AES_256_GCM,
        AES_256_CBC,
        RSA_2048,
        RSA_4096,
        ECDSA_P256,
        ECDSA_P384,
        CHACHA20_POLY1305,
        HMAC_SHA256,
        HMAC_SHA512
    }

    /**
     * Enum representing the status of the encryption key.
     */
    public enum KeyStatus {
        ACTIVE,
        INACTIVE,
        ROTATED,
        EXPIRED,
        REVOKED
    }

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (activatedAt == null) {
            activatedAt = LocalDateTime.now();
        }
    }
}
