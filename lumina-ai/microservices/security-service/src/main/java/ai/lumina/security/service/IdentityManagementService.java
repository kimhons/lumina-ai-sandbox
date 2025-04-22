package ai.lumina.security.service;

import ai.lumina.security.model.UserIdentity;
import ai.lumina.security.repository.UserIdentityRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Service for managing user identities and authentication.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class IdentityManagementService {

    private final UserIdentityRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    /**
     * Create a new user identity.
     *
     * @param user The user to create
     * @return The created user
     */
    @Transactional
    public UserIdentity createUser(UserIdentity user) {
        log.info("Creating user: {}", user.getUsername());
        // Hash the password before saving
        user.setPasswordHash(passwordEncoder.encode(user.getPasswordHash()));
        return userRepository.save(user);
    }

    /**
     * Update an existing user identity.
     *
     * @param id The user ID
     * @param user The updated user
     * @return The updated user
     */
    @Transactional
    public Optional<UserIdentity> updateUser(Long id, UserIdentity user) {
        log.info("Updating user with ID: {}", id);
        return userRepository.findById(id)
                .map(existingUser -> {
                    user.setId(id);
                    // Only update password if it has changed
                    if (!user.getPasswordHash().equals(existingUser.getPasswordHash())) {
                        user.setPasswordHash(passwordEncoder.encode(user.getPasswordHash()));
                        user.setPasswordChangedAt(LocalDateTime.now());
                    } else {
                        user.setPasswordHash(existingUser.getPasswordHash());
                        user.setPasswordChangedAt(existingUser.getPasswordChangedAt());
                    }
                    return userRepository.save(user);
                });
    }

    /**
     * Delete a user identity.
     *
     * @param id The user ID
     */
    @Transactional
    public void deleteUser(Long id) {
        log.info("Deleting user with ID: {}", id);
        userRepository.deleteById(id);
    }

    /**
     * Get a user identity by ID.
     *
     * @param id The user ID
     * @return The user if found
     */
    @Transactional(readOnly = true)
    public Optional<UserIdentity> getUserById(Long id) {
        return userRepository.findById(id);
    }

    /**
     * Get a user identity by username.
     *
     * @param username The username
     * @return The user if found
     */
    @Transactional(readOnly = true)
    public Optional<UserIdentity> getUserByUsername(String username) {
        return userRepository.findByUsername(username);
    }

    /**
     * Get a user identity by email.
     *
     * @param email The email
     * @return The user if found
     */
    @Transactional(readOnly = true)
    public Optional<UserIdentity> getUserByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    /**
     * Get all user identities.
     *
     * @return List of all users
     */
    @Transactional(readOnly = true)
    public List<UserIdentity> getAllUsers() {
        return userRepository.findAll();
    }

    /**
     * Get users by role.
     *
     * @param role The role
     * @return List of users with the role
     */
    @Transactional(readOnly = true)
    public List<UserIdentity> getUsersByRole(String role) {
        return userRepository.findByRole(role);
    }

    /**
     * Lock a user account.
     *
     * @param id The user ID
     * @return The updated user
     */
    @Transactional
    public Optional<UserIdentity> lockUserAccount(Long id) {
        log.info("Locking user account with ID: {}", id);
        return userRepository.findById(id)
                .map(user -> {
                    user.setAccountLocked(true);
                    return userRepository.save(user);
                });
    }

    /**
     * Unlock a user account.
     *
     * @param id The user ID
     * @return The updated user
     */
    @Transactional
    public Optional<UserIdentity> unlockUserAccount(Long id) {
        log.info("Unlocking user account with ID: {}", id);
        return userRepository.findById(id)
                .map(user -> {
                    user.setAccountLocked(false);
                    return userRepository.save(user);
                });
    }

    /**
     * Update a user's MFA settings.
     *
     * @param id The user ID
     * @param mfaType The MFA type
     * @param mfaSecret The MFA secret
     * @return The updated user
     */
    @Transactional
    public Optional<UserIdentity> updateMfaSettings(Long id, UserIdentity.MfaType mfaType, String mfaSecret) {
        log.info("Updating MFA settings for user with ID: {}", id);
        return userRepository.findById(id)
                .map(user -> {
                    user.setMfaType(mfaType);
                    user.setMfaSecret(mfaSecret);
                    return userRepository.save(user);
                });
    }
}
