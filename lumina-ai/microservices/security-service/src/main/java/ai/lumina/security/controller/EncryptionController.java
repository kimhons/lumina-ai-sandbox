package ai.lumina.security.controller;

import ai.lumina.security.model.EncryptionKey;
import ai.lumina.security.service.EncryptionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST controller for encryption operations.
 */
@RestController
@RequestMapping("/api/security/encryption")
@RequiredArgsConstructor
@Slf4j
public class EncryptionController {

    private final EncryptionService encryptionService;

    /**
     * Create a new encryption key.
     *
     * @param key The key to create
     * @return The created key
     */
    @PostMapping("/keys")
    public ResponseEntity<EncryptionKey> createKey(@RequestBody EncryptionKey key) {
        log.info("REST request to create encryption key: {}", key.getKeyName());
        EncryptionKey createdKey = encryptionService.createKey(key);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdKey);
    }

    /**
     * Update an existing encryption key.
     *
     * @param id The key ID
     * @param key The updated key
     * @return The updated key
     */
    @PutMapping("/keys/{id}")
    public ResponseEntity<EncryptionKey> updateKey(
            @PathVariable Long id,
            @RequestBody EncryptionKey key) {
        log.info("REST request to update encryption key with ID: {}", id);
        return encryptionService.updateKey(id, key)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Rotate an encryption key.
     *
     * @param id The key ID
     * @param newKeyMaterial The new key material
     * @return The rotated key
     */
    @PutMapping("/keys/{id}/rotate")
    public ResponseEntity<EncryptionKey> rotateKey(
            @PathVariable Long id,
            @RequestParam String newKeyMaterial) {
        log.info("REST request to rotate encryption key with ID: {}", id);
        return encryptionService.rotateKey(id, newKeyMaterial)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Revoke an encryption key.
     *
     * @param id The key ID
     * @param revokedBy The user who revoked the key
     * @return The revoked key
     */
    @PutMapping("/keys/{id}/revoke")
    public ResponseEntity<EncryptionKey> revokeKey(
            @PathVariable Long id,
            @RequestParam String revokedBy) {
        log.info("REST request to revoke encryption key with ID: {}", id);
        return encryptionService.revokeKey(id, revokedBy)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get an encryption key by ID.
     *
     * @param id The key ID
     * @return The key if found
     */
    @GetMapping("/keys/{id}")
    public ResponseEntity<EncryptionKey> getKey(@PathVariable Long id) {
        log.info("REST request to get encryption key with ID: {}", id);
        return encryptionService.getKeyById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get all encryption keys.
     *
     * @return List of all keys
     */
    @GetMapping("/keys")
    public ResponseEntity<List<EncryptionKey>> getAllKeys() {
        log.info("REST request to get all encryption keys");
        List<EncryptionKey> keys = encryptionService.getAllKeys();
        return ResponseEntity.ok(keys);
    }

    /**
     * Get keys by status.
     *
     * @param status The key status
     * @return List of matching keys
     */
    @GetMapping("/keys/by-status/{status}")
    public ResponseEntity<List<EncryptionKey>> getKeysByStatus(
            @PathVariable EncryptionKey.KeyStatus status) {
        log.info("REST request to get encryption keys by status: {}", status);
        List<EncryptionKey> keys = encryptionService.getKeysByStatus(status);
        return ResponseEntity.ok(keys);
    }

    /**
     * Encrypt data using a specified key.
     *
     * @param keyId The key ID
     * @param data The data to encrypt
     * @return The encrypted data
     */
    @PostMapping("/encrypt")
    public ResponseEntity<String> encrypt(
            @RequestParam String keyId,
            @RequestParam String data) {
        log.info("REST request to encrypt data using key: {}", keyId);
        String encryptedData = encryptionService.encrypt(keyId, data);
        return ResponseEntity.ok(encryptedData);
    }

    /**
     * Decrypt data using a specified key.
     *
     * @param keyId The key ID
     * @param encryptedData The encrypted data
     * @return The decrypted data
     */
    @PostMapping("/decrypt")
    public ResponseEntity<String> decrypt(
            @RequestParam String keyId,
            @RequestParam String encryptedData) {
        log.info("REST request to decrypt data using key: {}", keyId);
        String decryptedData = encryptionService.decrypt(keyId, encryptedData);
        return ResponseEntity.ok(decryptedData);
    }
}
