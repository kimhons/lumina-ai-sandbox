package ai.lumina.memory.repository;

import ai.lumina.memory.model.PersistentMemory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for persistent memory operations.
 */
@Repository
public interface PersistentMemoryRepository extends JpaRepository<PersistentMemory, UUID> {

    /**
     * Find a memory item by user ID and key.
     *
     * @param userId The user ID
     * @param key The memory key
     * @return The memory item if found
     */
    Optional<PersistentMemory> findByUserIdAndKey(String userId, String key);

    /**
     * Find all memory items for a user.
     *
     * @param userId The user ID
     * @return List of memory items for the user
     */
    List<PersistentMemory> findByUserId(String userId);

    /**
     * Find memory items by user ID and memory type.
     *
     * @param userId The user ID
     * @param memoryType The memory type
     * @return List of memory items of the specified type for the user
     */
    List<PersistentMemory> findByUserIdAndMemoryType(String userId, String memoryType);

    /**
     * Find memory items by user ID with importance score in the specified range.
     *
     * @param userId The user ID
     * @param minImportance The minimum importance score (inclusive)
     * @param maxImportance The maximum importance score (inclusive)
     * @return List of memory items with importance in the specified range
     */
    List<PersistentMemory> findByUserIdAndImportanceScoreBetween(String userId, Double minImportance, Double maxImportance);

    /**
     * Find the most frequently accessed memory items for a user.
     *
     * @param userId The user ID
     * @param limit Maximum number of items to return
     * @return List of most frequently accessed memory items
     */
    @Query("SELECT m FROM PersistentMemory m WHERE m.userId = :userId ORDER BY m.accessCount DESC")
    List<PersistentMemory> findMostAccessedByUserId(@Param("userId") String userId, @Param("limit") int limit);

    /**
     * Find the most recently accessed memory items for a user.
     *
     * @param userId The user ID
     * @param limit Maximum number of items to return
     * @return List of most recently accessed memory items
     */
    @Query("SELECT m FROM PersistentMemory m WHERE m.userId = :userId ORDER BY m.lastAccessed DESC")
    List<PersistentMemory> findMostRecentByUserId(@Param("userId") String userId, @Param("limit") int limit);

    /**
     * Find expired memory items.
     *
     * @param currentTime The current time
     * @return List of expired memory items
     */
    List<PersistentMemory> findByExpiresAtLessThan(LocalDateTime currentTime);

    /**
     * Delete expired memory items.
     *
     * @param currentTime The current time
     * @return Number of deleted items
     */
    int deleteByExpiresAtLessThan(LocalDateTime currentTime);
}
