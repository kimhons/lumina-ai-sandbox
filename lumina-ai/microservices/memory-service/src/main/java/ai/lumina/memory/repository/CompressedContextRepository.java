package ai.lumina.memory.repository;

import ai.lumina.memory.model.CompressedContext;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

/**
 * Repository for managing CompressedContext entities.
 */
@Repository
public interface CompressedContextRepository extends JpaRepository<CompressedContext, UUID> {

    /**
     * Find compressed contexts by user ID
     * 
     * @param userId The user ID
     * @return List of compressed contexts for the user
     */
    List<CompressedContext> findByUserId(String userId);
    
    /**
     * Find compressed contexts by session ID
     * 
     * @param sessionId The session ID
     * @return List of compressed contexts for the session
     */
    List<CompressedContext> findBySessionId(String sessionId);
    
    /**
     * Find compressed contexts by user ID and session ID
     * 
     * @param userId The user ID
     * @param sessionId The session ID
     * @return List of compressed contexts for the user and session
     */
    List<CompressedContext> findByUserIdAndSessionId(String userId, String sessionId);
    
    /**
     * Find compressed contexts by compression method
     * 
     * @param compressionMethod The compression method
     * @return List of compressed contexts using the specified compression method
     */
    List<CompressedContext> findByCompressionMethod(String compressionMethod);
    
    /**
     * Find compressed contexts with compression ratio less than the specified value
     * 
     * @param ratio The maximum compression ratio
     * @return List of compressed contexts with compression ratio less than the specified value
     */
    List<CompressedContext> findByCompressionRatioLessThan(Double ratio);
    
    /**
     * Find compressed contexts created after the specified date
     * 
     * @param date The date
     * @return List of compressed contexts created after the specified date
     */
    List<CompressedContext> findByCreatedAtAfter(LocalDateTime date);
    
    /**
     * Find the most recent compressed context for a session
     * 
     * @param sessionId The session ID
     * @return The most recent compressed context for the session
     */
    @Query("SELECT c FROM CompressedContext c WHERE c.sessionId = :sessionId ORDER BY c.createdAt DESC LIMIT 1")
    CompressedContext findMostRecentBySessionId(@Param("sessionId") String sessionId);
    
    /**
     * Find compressed contexts with token reduction greater than the specified percentage
     * 
     * @param percentage The minimum token reduction percentage (0-1)
     * @return List of compressed contexts with token reduction greater than the specified percentage
     */
    @Query("SELECT c FROM CompressedContext c WHERE (c.originalTokenCount - c.compressedTokenCount) / c.originalTokenCount >= :percentage")
    List<CompressedContext> findByTokenReductionGreaterThan(@Param("percentage") Double percentage);
}
