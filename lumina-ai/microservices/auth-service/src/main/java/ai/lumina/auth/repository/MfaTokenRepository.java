package ai.lumina.auth.repository;

import ai.lumina.auth.model.MfaToken;
import ai.lumina.auth.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface MfaTokenRepository extends JpaRepository<MfaToken, Long> {
    
    Optional<MfaToken> findByToken(String token);
    
    List<MfaToken> findByUserAndTokenTypeAndUsedFalseAndExpiresAtAfter(
            User user, 
            MfaToken.MfaTokenType tokenType, 
            LocalDateTime now);
    
    void deleteByExpiresAtBefore(LocalDateTime dateTime);
    
    void deleteByUserAndTokenType(User user, MfaToken.MfaTokenType tokenType);
}
