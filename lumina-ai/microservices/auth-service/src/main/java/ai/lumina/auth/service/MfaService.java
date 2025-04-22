package ai.lumina.auth.service;

import ai.lumina.auth.model.MfaToken;
import ai.lumina.auth.model.User;
import ai.lumina.auth.repository.MfaTokenRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class MfaService {

    private final MfaTokenRepository mfaTokenRepository;
    private final SecureRandom secureRandom = new SecureRandom();
    
    @Value("${app.mfa.token.expiration:300}") // 5 minutes default
    private int tokenExpirationSeconds;
    
    @Value("${app.mfa.totp.issuer:LuminaAI}")
    private String totpIssuer;

    /**
     * Generate a new MFA token for the specified user and token type
     */
    @Transactional
    public MfaToken generateToken(User user, MfaToken.MfaTokenType tokenType) {
        // Generate a random token
        byte[] randomBytes = new byte[32];
        secureRandom.nextBytes(randomBytes);
        String token = Base64.getUrlEncoder().withoutPadding().encodeToString(randomBytes);
        
        // Create and save the token
        MfaToken mfaToken = MfaToken.builder()
                .user(user)
                .token(token)
                .tokenType(tokenType)
                .expiresAt(LocalDateTime.now().plusSeconds(tokenExpirationSeconds))
                .used(false)
                .build();
        
        return mfaTokenRepository.save(mfaToken);
    }
    
    /**
     * Verify an MFA token
     */
    @Transactional
    public boolean verifyToken(String token) {
        Optional<MfaToken> mfaTokenOpt = mfaTokenRepository.findByToken(token);
        
        if (mfaTokenOpt.isEmpty()) {
            return false;
        }
        
        MfaToken mfaToken = mfaTokenOpt.get();
        
        if (!mfaToken.isValid()) {
            return false;
        }
        
        // Mark the token as used
        mfaToken.setUsed(true);
        mfaTokenRepository.save(mfaToken);
        
        return true;
    }
    
    /**
     * Generate a TOTP secret for a user
     */
    public String generateTotpSecret() {
        byte[] secretBytes = new byte[20]; // 160 bits as recommended for TOTP
        secureRandom.nextBytes(secretBytes);
        return Base64.getEncoder().encodeToString(secretBytes);
    }
    
    /**
     * Get the TOTP URI for QR code generation
     */
    public String getTotpUri(User user, String secret) {
        return String.format("otpauth://totp/%s:%s?secret=%s&issuer=%s",
                totpIssuer, user.getUsername(), secret, totpIssuer);
    }
    
    /**
     * Verify a TOTP code
     */
    public boolean verifyTotp(String secret, String code) {
        // In a real implementation, this would use a TOTP library to verify the code
        // For this example, we'll just return true to simulate successful verification
        return true;
    }
    
    /**
     * Get active tokens for a user and token type
     */
    @Transactional(readOnly = true)
    public List<MfaToken> getActiveTokens(User user, MfaToken.MfaTokenType tokenType) {
        return mfaTokenRepository.findByUserAndTokenTypeAndUsedFalseAndExpiresAtAfter(
                user, tokenType, LocalDateTime.now());
    }
    
    /**
     * Clean up expired tokens
     */
    @Transactional
    public void cleanupExpiredTokens() {
        mfaTokenRepository.deleteByExpiresAtBefore(LocalDateTime.now());
    }
    
    /**
     * Invalidate all tokens of a specific type for a user
     */
    @Transactional
    public void invalidateTokens(User user, MfaToken.MfaTokenType tokenType) {
        mfaTokenRepository.deleteByUserAndTokenType(user, tokenType);
    }
}
