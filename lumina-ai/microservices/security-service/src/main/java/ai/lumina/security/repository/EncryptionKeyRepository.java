package ai.lumina.security.repository;

import ai.lumina.security.model.EncryptionKey;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Repository interface for managing EncryptionKey entities.
 */
@Repository
public interface EncryptionKeyRepository extends JpaRepository<EncryptionKey, Long> {

    /**
     * Find a key by its ID.
     *
     * @param keyId The key ID
     * @return The key if found
     */
    Optional<EncryptionKey> findByKeyId(String keyId);

    /**
     * Find keys by name.
     *
     * @param keyName The key name
     * @return List of matching keys
     */
    List<EncryptionKey> findByKeyName(String keyName);

    /**
     * Find keys by type.
     *
     * @param keyType The key type
     * @return List of matching keys
     */
    List<EncryptionKey> findByKeyType(EncryptionKey.KeyType keyType);

    /**
     * Find keys by algorithm.
     *
     * @param algorithm The algorithm
     * @return List of matching keys
     */
    List<EncryptionKey> findByAlgorithm(EncryptionKey.Algorithm algorithm);

    /**
     * Find keys by status.
     *
     * @param status The key status
     * @return List of matching keys
     */
    List<EncryptionKey> findByStatus(EncryptionKey.KeyStatus status);

    /**
     * Find keys by purpose.
     *
     * @param purpose The key purpose
     * @return List of matching keys
     */
    List<EncryptionKey> findByPurpose(String purpose);

    /**
     * Find keys created by a specific user.
     *
     * @param createdBy The creator's identifier
     * @return List of matching keys
     */
    List<EncryptionKey> findByCreatedBy(String createdBy);

    /**
     * Find keys that expire before a specific date.
     *
     * @param expiryDate The expiry date
     * @return List of matching keys
     */
    List<EncryptionKey> findByExpiresAtBefore(LocalDateTime expiryDate);

    /**
     * Find keys created after a specific date.
     *
     * @param creationDate The creation date
     * @return List of matching keys
     */
    List<EncryptionKey> findByCreatedAtAfter(LocalDateTime creationDate);

    /**
     * Find active keys for a specific purpose.
     *
     * @param purpose The key purpose
     * @return List of matching keys
     */
    List<EncryptionKey> findByStatusAndPurpose(EncryptionKey.KeyStatus status, String purpose);
}
