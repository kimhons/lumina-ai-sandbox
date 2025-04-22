package ai.lumina.memory.repository;

import ai.lumina.memory.model.Topic;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for managing Topic entities in the hierarchical memory system.
 */
@Repository
public interface TopicRepository extends JpaRepository<Topic, UUID> {

    /**
     * Find topics by user ID
     * 
     * @param userId The user ID
     * @return List of topics for the user
     */
    List<Topic> findByUserId(String userId);
    
    /**
     * Find topics by name containing the specified text
     * 
     * @param name The text to search for in topic names
     * @return List of topics with names containing the specified text
     */
    List<Topic> findByNameContainingIgnoreCase(String name);
    
    /**
     * Find topics by parent ID
     * 
     * @param parentId The parent topic ID
     * @return List of child topics for the specified parent
     */
    @Query("SELECT t FROM Topic t WHERE t.parent.id = :parentId")
    List<Topic> findByParentId(@Param("parentId") UUID parentId);
    
    /**
     * Find root topics (topics with no parent)
     * 
     * @return List of root topics
     */
    List<Topic> findByParentIsNull();
    
    /**
     * Find root topics for a specific user
     * 
     * @param userId The user ID
     * @return List of root topics for the user
     */
    List<Topic> findByUserIdAndParentIsNull(String userId);
    
    /**
     * Find topics by importance score greater than the specified value
     * 
     * @param importanceScore The minimum importance score
     * @return List of topics with importance score greater than the specified value
     */
    List<Topic> findByImportanceScoreGreaterThanEqual(Double importanceScore);
    
    /**
     * Find the topic hierarchy path from root to the specified topic
     * 
     * @param topicId The topic ID
     * @return List of topics in the path from root to the specified topic
     */
    @Query(value = "WITH RECURSIVE topic_path AS (" +
            "  SELECT t.*, 1 AS level FROM memory_topics t WHERE t.id = :topicId " +
            "  UNION ALL " +
            "  SELECT t.*, tp.level + 1 FROM memory_topics t " +
            "  JOIN topic_path tp ON t.id = tp.parent_id " +
            ") " +
            "SELECT * FROM topic_path ORDER BY level DESC", nativeQuery = true)
    List<Topic> findTopicPath(@Param("topicId") UUID topicId);
    
    /**
     * Count the number of child topics for a parent topic
     * 
     * @param parentId The parent topic ID
     * @return The number of child topics
     */
    @Query("SELECT COUNT(t) FROM Topic t WHERE t.parent.id = :parentId")
    Long countByParentId(@Param("parentId") UUID parentId);
}
