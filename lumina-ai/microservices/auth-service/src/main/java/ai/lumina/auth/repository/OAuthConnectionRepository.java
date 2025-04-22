package ai.lumina.auth.repository;

import ai.lumina.auth.model.OAuthConnection;
import ai.lumina.auth.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface OAuthConnectionRepository extends JpaRepository<OAuthConnection, Long> {
    
    Optional<OAuthConnection> findByProviderAndProviderUserId(String provider, String providerUserId);
    
    List<OAuthConnection> findByUser(User user);
    
    List<OAuthConnection> findByUserAndProvider(User user, String provider);
    
    boolean existsByUserAndProvider(User user, String provider);
    
    void deleteByUserAndProvider(User user, String provider);
}
