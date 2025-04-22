package ai.lumina.auth.controller;

import ai.lumina.auth.dto.LoginRequest;
import ai.lumina.auth.dto.MfaSetupResponse;
import ai.lumina.auth.dto.RegisterRequest;
import ai.lumina.auth.dto.TokenResponse;
import ai.lumina.auth.model.User;
import ai.lumina.auth.service.JwtService;
import ai.lumina.auth.service.MfaService;
import ai.lumina.auth.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final UserService userService;
    private final JwtService jwtService;
    private final MfaService mfaService;

    @PostMapping("/register")
    public ResponseEntity<?> register(@Valid @RequestBody RegisterRequest request) {
        try {
            User user = User.builder()
                    .username(request.getUsername())
                    .email(request.getEmail())
                    .password(request.getPassword())
                    .firstName(request.getFirstName())
                    .lastName(request.getLastName())
                    .build();
            
            userService.createUser(user);
            
            return ResponseEntity.status(HttpStatus.CREATED).build();
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequest request) {
        try {
            // Authenticate with username and password
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
            );
            
            // Get user details
            User user = userService.getUserByUsername(request.getUsername())
                    .orElseThrow(() -> new IllegalArgumentException("User not found"));
            
            // Check if MFA is enabled
            if (user.isMfaEnabled()) {
                // If MFA code is not provided, return a challenge
                if (request.getMfaCode() == null || request.getMfaCode().isEmpty()) {
                    return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                            .header("X-MFA-Required", "true")
                            .build();
                }
                
                // Verify MFA code
                boolean isValidMfa = mfaService.verifyTotp(user.getMfaSecret(), request.getMfaCode());
                if (!isValidMfa) {
                    return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                            .body("Invalid MFA code");
                }
            }
            
            // Generate JWT token
            SecurityContextHolder.getContext().setAuthentication(authentication);
            TokenResponse tokenResponse = jwtService.generateToken(authentication);
            
            return ResponseEntity.ok(tokenResponse);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body("Authentication failed: " + e.getMessage());
        }
    }

    @PostMapping("/refresh")
    public ResponseEntity<?> refreshToken(@RequestHeader("Authorization") String refreshToken) {
        try {
            if (refreshToken == null || !refreshToken.startsWith("Bearer ")) {
                return ResponseEntity.badRequest().body("Invalid refresh token format");
            }
            
            refreshToken = refreshToken.substring(7);
            
            if (!jwtService.validateToken(refreshToken)) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Invalid refresh token");
            }
            
            String username = jwtService.extractUsername(refreshToken);
            UserDetails userDetails = userService.loadUserByUsername(username);
            
            TokenResponse tokenResponse = jwtService.generateToken(userDetails);
            
            return ResponseEntity.ok(tokenResponse);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body("Token refresh failed: " + e.getMessage());
        }
    }

    @PostMapping("/mfa/setup")
    public ResponseEntity<?> setupMfa() {
        try {
            // Get current authenticated user
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            String username = authentication.getName();
            
            User user = userService.getUserByUsername(username)
                    .orElseThrow(() -> new IllegalArgumentException("User not found"));
            
            // Generate TOTP secret
            String secret = mfaService.generateTotpSecret();
            
            // Generate QR code URI
            String qrCodeUri = mfaService.getTotpUri(user, secret);
            
            // Generate backup codes (in a real implementation)
            String backupCodes = "Use the authenticator app for MFA";
            
            MfaSetupResponse response = MfaSetupResponse.builder()
                    .secret(secret)
                    .qrCodeUri(qrCodeUri)
                    .backupCodes(backupCodes)
                    .build();
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("MFA setup failed: " + e.getMessage());
        }
    }

    @PostMapping("/mfa/enable")
    public ResponseEntity<?> enableMfa(@RequestParam String secret, @RequestParam String code) {
        try {
            // Get current authenticated user
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            String username = authentication.getName();
            
            User user = userService.getUserByUsername(username)
                    .orElseThrow(() -> new IllegalArgumentException("User not found"));
            
            // Verify the provided code
            boolean isValidCode = mfaService.verifyTotp(secret, code);
            if (!isValidCode) {
                return ResponseEntity.badRequest().body("Invalid verification code");
            }
            
            // Enable MFA for the user
            userService.enableMfa(user.getId(), secret);
            
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("MFA enablement failed: " + e.getMessage());
        }
    }

    @PostMapping("/mfa/disable")
    public ResponseEntity<?> disableMfa() {
        try {
            // Get current authenticated user
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            String username = authentication.getName();
            
            User user = userService.getUserByUsername(username)
                    .orElseThrow(() -> new IllegalArgumentException("User not found"));
            
            // Disable MFA for the user
            userService.disableMfa(user.getId());
            
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("MFA disablement failed: " + e.getMessage());
        }
    }
}
