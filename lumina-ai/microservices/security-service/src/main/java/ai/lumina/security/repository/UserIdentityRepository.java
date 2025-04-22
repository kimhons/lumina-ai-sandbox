package ai.lumina.security.repository;

import ai.lumina.security.model.UserIdentity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Repository interface for managing UserIdentity entities.
 */
@Repository
public interface UserIdentityRepository extends JpaRepository<UserIdentity, Long> {

    /**
     * Find a user by username.
     *
     * @param username The username
     * @return The user if found
     */
    Optional<UserIdentity> findByUsername(String username);

    /**
     * Find a user by email.
     *
     * @param email The email address
     * @return The user if found
     */
    Optional<UserIdentity> findByEmail(String email);

    /**
     * Find all users with a specific role.
     *
     * @param role The role name
     * @return List of users with the role
     */
    @Query("SELECT u FROM UserIdentity u JOIN u.roles r WHERE r = :role")
    List<UserIdentity> findByRole(String role);

    /**
     * Find all enabled users.
     *
     * @return List of enabled users
     */
    List<UserIdentity> findByEnabledTrue();

    /**
     * Find all users with locked accounts.
     *
     * @return List of locked users
     */
    List<UserIdentity> findByAccountLockedTrue();

    /**
     * Find all users with expired accounts.
     *
     * @return List of users with expired accounts
     */
    List<UserIdentity> findByAccountExpiredTrue();

    /**
     * Find all users with expired credentials.
     *
     * @return List of users with expired credentials
     */
    List<UserIdentity> findByCredentialsExpiredTrue();

    /**
     * Find users who haven't logged in since a specific date.
     *
     * @param date The cutoff date
     * @return List of inactive users
     */
    List<UserIdentity> findByLastLoginAtBefore(LocalDateTime date);

    /**
     * Find users who need to change their password (password older than a specific date).
     *
     * @param date The cutoff date
     * @return List of users needing password change
     */
    List<UserIdentity> findByPasswordChangedAtBefore(LocalDateTime date);

    /**
     * Find users by MFA type.
     *
     * @param mfaType The MFA type
     * @return List of users with the specified MFA type
     */
    List<UserIdentity> findByMfaType(UserIdentity.MfaType mfaType);
}
