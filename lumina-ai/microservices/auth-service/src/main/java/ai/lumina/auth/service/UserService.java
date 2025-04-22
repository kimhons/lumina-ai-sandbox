package ai.lumina.auth.service;

import ai.lumina.auth.model.User;
import ai.lumina.auth.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class UserService implements UserDetailsService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final RoleService roleService;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("User not found with username: " + username));
        
        return org.springframework.security.core.userdetails.User.builder()
                .username(user.getUsername())
                .password(user.getPassword())
                .disabled(!user.isEnabled())
                .accountExpired(false)
                .credentialsExpired(false)
                .accountLocked(false)
                .authorities(roleService.getAuthorities(user.getRoles()))
                .build();
    }

    @Transactional
    public User createUser(User user) {
        if (userRepository.existsByUsername(user.getUsername())) {
            throw new IllegalArgumentException("Username already exists");
        }
        
        if (userRepository.existsByEmail(user.getEmail())) {
            throw new IllegalArgumentException("Email already exists");
        }
        
        // Encode password
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        
        // Set default values
        user.setEnabled(true);
        user.setEmailVerified(false);
        user.setMfaEnabled(false);
        
        // Assign default role if none provided
        if (user.getRoles() == null || user.getRoles().isEmpty()) {
            user.getRoles().add(roleService.getOrCreateRole("USER"));
        }
        
        return userRepository.save(user);
    }

    @Transactional(readOnly = true)
    public Optional<User> getUserById(Long id) {
        return userRepository.findById(id);
    }

    @Transactional(readOnly = true)
    public Optional<User> getUserByUsername(String username) {
        return userRepository.findByUsername(username);
    }

    @Transactional(readOnly = true)
    public Optional<User> getUserByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    @Transactional(readOnly = true)
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    @Transactional
    public User updateUser(User user) {
        return userRepository.save(user);
    }

    @Transactional
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }

    @Transactional
    public boolean enableMfa(Long userId, String mfaSecret) {
        return userRepository.findById(userId).map(user -> {
            user.setMfaEnabled(true);
            user.setMfaSecret(mfaSecret);
            userRepository.save(user);
            return true;
        }).orElse(false);
    }

    @Transactional
    public boolean disableMfa(Long userId) {
        return userRepository.findById(userId).map(user -> {
            user.setMfaEnabled(false);
            user.setMfaSecret(null);
            userRepository.save(user);
            return true;
        }).orElse(false);
    }

    @Transactional
    public boolean verifyEmail(Long userId) {
        return userRepository.findById(userId).map(user -> {
            user.setEmailVerified(true);
            userRepository.save(user);
            return true;
        }).orElse(false);
    }
}
