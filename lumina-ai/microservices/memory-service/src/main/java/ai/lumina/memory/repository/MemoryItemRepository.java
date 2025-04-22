package ai.lumina.memory.repository;

import ai.lumina.memory.model.MemoryItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for managing MemoryItem entities.
 */
@Repository
public interface MemoryItemRepository extends JpaRepository<MemoryItem, UUID> {

    /**
     * Find memory items by user ID
     * 
     * @param userId The user ID
     * @return List of memory items for the user
     */
    List<MemoryItem> findByUserId(String userId);
    
    /**
     * Find memory items by session ID
     * 
     * @param sessionId The session ID
     * @return List of memory items for the session
     */
    List<MemoryItem> findBySessionId(String sessionId);
    
    /**
     * Find memory items by user ID and session ID
     * 
     * @param userId The user ID
     * @param sessionId The session ID
     * @return List of memory items for the user and session
     */
    List<MemoryItem> findByUserIdAndSessionId(String userId, String sessionId);
    
    /**
     * Find memory items by importance score greater than the specified value
     * 
     * @param importanceScore The minimum importance score
     * @return List of memory items with importance score greater than the specified value
     */
    List<MemoryItem> findByImportanceScoreGreaterThanEqual(Double importanceScore);
    
    /**
     * Find memory items created after the specified date
     * 
     * @param date The date
     * @return List of memory items created after the specified date
     */
    List<MemoryItem> findByCreatedAtAfter(LocalDateTime date);
    
    /**
     * Find memory items that have not expired
     * 
     * @param now The current date/time
     * @return List of memory items that have not expired
     */
    List<MemoryItem> findByExpiresAtIsNullOrExpiresAtGreaterThan(LocalDateTime now);
    
    /**
     * Find memory items by user ID that have not expired
     * 
     * @param userId The user ID
     * @param now The current date/time
     * @return List of memory items for the user that have not expired
     */
    List<MemoryItem> findByUserIdAndExpiresAtIsNullOrUserIdAndExpiresAtGreaterThan(
            String userId, String userIdSame, LocalDateTime now);
    
    /**
     * Search for memory items containing the specified text
     * 
     * @param searchText The text to search for
     * @return List of memory items containing the specified text
     */
    @Query("SELECT m FROM MemoryItem m WHERE LOWER(m.content) LIKE LOWER(CONCAT('%', :searchText, '%'))")
    List<MemoryItem> searchByContent(@Param("searchText") String searchText);
    
    /**
     * Find the most recent memory items for a user, limited by count
     * 
     * @param userId The user ID
     * @param limit The maximum number of items to return
     * @return List of the most recent memory items for the user
     */
    @Query("SELECT m FROM MemoryItem m WHERE m.userId = :userId ORDER BY m.createdAt DESC LIMIT :limit")
    List<MemoryItem> findMostRecentByUserId(@Param("userId") String userId, @Param("limit") int limit);
}
