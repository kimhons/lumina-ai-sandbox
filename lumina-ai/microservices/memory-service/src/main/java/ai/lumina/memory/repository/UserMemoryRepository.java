package ai.lumina.memory.repository;

import ai.lumina.memory.model.UserMemory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for managing UserMemory entities in the cross-session memory system.
 */
@Repository
public interface UserMemoryRepository extends JpaRepository<UserMemory, UUID> {

    /**
     * Find user memories by user ID
     * 
     * @param userId The user ID
     * @return List of memories for the user
     */
    List<UserMemory> findByUserId(String userId);
    
    /**
     * Find user memory by user ID and key
     * 
     * @param userId The user ID
     * @param key The memory key
     * @return The user memory if found
     */
    Optional<UserMemory> findByUserIdAndKey(String userId, String key);
    
    /**
     * Find user memories by memory type
     * 
     * @param userId The user ID
     * @param memoryType The memory type
     * @return List of memories of the specified type for the user
     */
    List<UserMemory> findByUserIdAndMemoryType(String userId, String memoryType);
    
    /**
     * Find user memories that have not expired
     * 
     * @param userId The user ID
     * @param now The current date/time
     * @return List of memories for the user that have not expired
     */
    List<UserMemory> findByUserIdAndExpiresAtIsNullOrUserIdAndExpiresAtGreaterThan(
            String userId, String userIdSame, LocalDateTime now);
    
    /**
     * Find user memories by last accessed date before the specified date
     * 
     * @param date The date
     * @return List of memories last accessed before the specified date
     */
    List<UserMemory> findByLastAccessedBefore(LocalDateTime date);
    
    /**
     * Find user memories by importance score greater than the specified value
     * 
     * @param userId The user ID
     * @param importanceScore The minimum importance score
     * @return List of memories with importance score greater than the specified value
     */
    List<UserMemory> findByUserIdAndImportanceScoreGreaterThanEqual(String userId, Double importanceScore);
    
    /**
     * Find the most frequently accessed memories for a user
     * 
     * @param userId The user ID
     * @param limit The maximum number of memories to return
     * @return List of the most frequently accessed memories for the user
     */
    @Query("SELECT m FROM UserMemory m WHERE m.userId = :userId ORDER BY m.accessCount DESC LIMIT :limit")
    List<UserMemory> findMostFrequentlyAccessedByUserId(@Param("userId") String userId, @Param("limit") int limit);
    
    /**
     * Find the most recently accessed memories for a user
     * 
     * @param userId The user ID
     * @param limit The maximum number of memories to return
     * @return List of the most recently accessed memories for the user
     */
    @Query("SELECT m FROM UserMemory m WHERE m.userId = :userId ORDER BY m.lastAccessed DESC LIMIT :limit")
    List<UserMemory> findMostRecentlyAccessedByUserId(@Param("userId") String userId, @Param("limit") int limit);
    
    /**
     * Search for user memories containing the specified text in the value
     * 
     * @param userId The user ID
     * @param searchText The text to search for
     * @return List of memories containing the specified text
     */
    @Query("SELECT m FROM UserMemory m WHERE m.userId = :userId AND LOWER(m.value) LIKE LOWER(CONCAT('%', :searchText, '%'))")
    List<UserMemory> searchByValue(@Param("userId") String userId, @Param("searchText") String searchText);
}
