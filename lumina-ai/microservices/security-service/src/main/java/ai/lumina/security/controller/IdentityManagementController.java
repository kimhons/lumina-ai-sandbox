package ai.lumina.security.controller;

import ai.lumina.security.model.UserIdentity;
import ai.lumina.security.service.IdentityManagementService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST controller for identity management operations.
 */
@RestController
@RequestMapping("/api/security/identity")
@RequiredArgsConstructor
@Slf4j
public class IdentityManagementController {

    private final IdentityManagementService identityService;

    /**
     * Create a new user identity.
     *
     * @param user The user to create
     * @return The created user
     */
    @PostMapping("/users")
    public ResponseEntity<UserIdentity> createUser(@RequestBody UserIdentity user) {
        log.info("REST request to create user: {}", user.getUsername());
        UserIdentity createdUser = identityService.createUser(user);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdUser);
    }

    /**
     * Update an existing user identity.
     *
     * @param id The user ID
     * @param user The updated user
     * @return The updated user
     */
    @PutMapping("/users/{id}")
    public ResponseEntity<UserIdentity> updateUser(
            @PathVariable Long id,
            @RequestBody UserIdentity user) {
        log.info("REST request to update user with ID: {}", id);
        return identityService.updateUser(id, user)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Delete a user identity.
     *
     * @param id The user ID
     * @return No content response
     */
    @DeleteMapping("/users/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        log.info("REST request to delete user with ID: {}", id);
        identityService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }

    /**
     * Get a user identity by ID.
     *
     * @param id The user ID
     * @return The user if found
     */
    @GetMapping("/users/{id}")
    public ResponseEntity<UserIdentity> getUser(@PathVariable Long id) {
        log.info("REST request to get user with ID: {}", id);
        return identityService.getUserById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get all user identities.
     *
     * @return List of all users
     */
    @GetMapping("/users")
    public ResponseEntity<List<UserIdentity>> getAllUsers() {
        log.info("REST request to get all users");
        List<UserIdentity> users = identityService.getAllUsers();
        return ResponseEntity.ok(users);
    }

    /**
     * Get users by role.
     *
     * @param role The role
     * @return List of users with the role
     */
    @GetMapping("/users/by-role/{role}")
    public ResponseEntity<List<UserIdentity>> getUsersByRole(@PathVariable String role) {
        log.info("REST request to get users by role: {}", role);
        List<UserIdentity> users = identityService.getUsersByRole(role);
        return ResponseEntity.ok(users);
    }

    /**
     * Lock a user account.
     *
     * @param id The user ID
     * @return The updated user
     */
    @PutMapping("/users/{id}/lock")
    public ResponseEntity<UserIdentity> lockUserAccount(@PathVariable Long id) {
        log.info("REST request to lock user account with ID: {}", id);
        return identityService.lockUserAccount(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Unlock a user account.
     *
     * @param id The user ID
     * @return The updated user
     */
    @PutMapping("/users/{id}/unlock")
    public ResponseEntity<UserIdentity> unlockUserAccount(@PathVariable Long id) {
        log.info("REST request to unlock user account with ID: {}", id);
        return identityService.unlockUserAccount(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Update a user's MFA settings.
     *
     * @param id The user ID
     * @param mfaType The MFA type
     * @param mfaSecret The MFA secret
     * @return The updated user
     */
    @PutMapping("/users/{id}/mfa")
    public ResponseEntity<UserIdentity> updateMfaSettings(
            @PathVariable Long id,
            @RequestParam UserIdentity.MfaType mfaType,
            @RequestParam(required = false) String mfaSecret) {
        log.info("REST request to update MFA settings for user with ID: {}", id);
        return identityService.updateMfaSettings(id, mfaType, mfaSecret)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
