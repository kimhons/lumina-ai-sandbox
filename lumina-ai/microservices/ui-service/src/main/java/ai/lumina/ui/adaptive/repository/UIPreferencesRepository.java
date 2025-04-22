package ai.lumina.ui.adaptive.repository;

import ai.lumina.ui.adaptive.model.UIPreferences;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Repository for managing UI preferences in the database
 */
@Repository
public interface UIPreferencesRepository extends JpaRepository<UIPreferences, Long> {
    
    /**
     * Find preferences by user ID
     * 
     * @param userId The ID of the user
     * @return Optional containing the user's preferences if found
     */
    Optional<UIPreferences> findByUserId(String userId);
    
    /**
     * Delete preferences by user ID
     * 
     * @param userId The ID of the user
     */
    void deleteByUserId(String userId);
}
