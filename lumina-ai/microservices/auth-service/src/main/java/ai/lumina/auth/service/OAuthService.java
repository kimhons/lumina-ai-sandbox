package ai.lumina.auth.service;

import ai.lumina.auth.model.OAuthConnection;
import ai.lumina.auth.model.User;
import ai.lumina.auth.repository.OAuthConnectionRepository;
import ai.lumina.auth.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class OAuthService {

    private final OAuthConnectionRepository oAuthConnectionRepository;
    private final UserRepository userRepository;
    private final RoleService roleService;

    /**
     * Find a user by OAuth provider and provider user ID
     */
    @Transactional(readOnly = true)
    public Optional<User> findUserByOAuth(String provider, String providerUserId) {
        return oAuthConnectionRepository.findByProviderAndProviderUserId(provider, providerUserId)
                .map(OAuthConnection::getUser);
    }

    /**
     * Create or update an OAuth connection for a user
     */
    @Transactional
    public OAuthConnection createOrUpdateConnection(User user, String provider, String providerUserId,
                                                   String accessToken, String refreshToken,
                                                   LocalDateTime tokenExpiresAt) {
        // Check if connection already exists
        Optional<OAuthConnection> existingConnection = oAuthConnectionRepository
                .findByProviderAndProviderUserId(provider, providerUserId);

        if (existingConnection.isPresent()) {
            // Update existing connection
            OAuthConnection connection = existingConnection.get();
            connection.setAccessToken(accessToken);
            connection.setRefreshToken(refreshToken);
            connection.setTokenExpiresAt(tokenExpiresAt);
            return oAuthConnectionRepository.save(connection);
        } else {
            // Create new connection
            OAuthConnection connection = OAuthConnection.builder()
                    .user(user)
                    .provider(provider)
                    .providerUserId(providerUserId)
                    .accessToken(accessToken)
                    .refreshToken(refreshToken)
                    .tokenExpiresAt(tokenExpiresAt)
                    .build();
            return oAuthConnectionRepository.save(connection);
        }
    }

    /**
     * Create a new user from OAuth data and create a connection
     */
    @Transactional
    public User createUserFromOAuth(String provider, String providerUserId, String email,
                                   String firstName, String lastName, String accessToken,
                                   String refreshToken, LocalDateTime tokenExpiresAt) {
        // Check if user with this email already exists
        Optional<User> existingUser = userRepository.findByEmail(email);

        User user;
        if (existingUser.isPresent()) {
            user = existingUser.get();
        } else {
            // Create new user
            user = User.builder()
                    .username(email) // Use email as username for OAuth users
                    .email(email)
                    .firstName(firstName)
                    .lastName(lastName)
                    .password("") // OAuth users don't have a password
                    .enabled(true)
                    .emailVerified(true) // Email is verified through OAuth provider
                    .mfaEnabled(false)
                    .build();

            // Add default role
            user.getRoles().add(roleService.getOrCreateRole("USER"));
            
            user = userRepository.save(user);
        }

        // Create OAuth connection
        createOrUpdateConnection(user, provider, providerUserId, accessToken, refreshToken, tokenExpiresAt);

        return user;
    }

    /**
     * Get all OAuth connections for a user
     */
    @Transactional(readOnly = true)
    public List<OAuthConnection> getUserConnections(User user) {
        return oAuthConnectionRepository.findByUser(user);
    }

    /**
     * Get all OAuth connections for a user and provider
     */
    @Transactional(readOnly = true)
    public List<OAuthConnection> getUserConnectionsByProvider(User user, String provider) {
        return oAuthConnectionRepository.findByUserAndProvider(user, provider);
    }

    /**
     * Check if a user has a connection to a specific provider
     */
    @Transactional(readOnly = true)
    public boolean hasProviderConnection(User user, String provider) {
        return oAuthConnectionRepository.existsByUserAndProvider(user, provider);
    }

    /**
     * Remove a provider connection for a user
     */
    @Transactional
    public void removeProviderConnection(User user, String provider) {
        oAuthConnectionRepository.deleteByUserAndProvider(user, provider);
    }
}
