package ai.lumina.learning.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import ai.lumina.learning.model.KnowledgeItem;

/**
 * Repository interface for KnowledgeItem entities.
 * Provides CRUD operations and custom queries for knowledge items.
 */
@Repository
public interface KnowledgeItemRepository extends JpaRepository<KnowledgeItem, String> {
    
    /**
     * Find knowledge items by type.
     * 
     * @param type The knowledge type
     * @return List of knowledge items with the specified type
     */
    Iterable<KnowledgeItem> findByType(KnowledgeItem.KnowledgeType type);
    
    /**
     * Find knowledge items by status.
     * 
     * @param status The knowledge status
     * @return List of knowledge items with the specified status
     */
    Iterable<KnowledgeItem> findByStatus(KnowledgeItem.KnowledgeStatus status);
    
    /**
     * Find knowledge items by name containing the specified string.
     * 
     * @param name The name substring to search for
     * @return List of knowledge items with names containing the specified string
     */
    Iterable<KnowledgeItem> findByNameContaining(String name);
    
    /**
     * Find knowledge items by source agent ID.
     * 
     * @param sourceAgentId The source agent ID
     * @return List of knowledge items from the specified source agent
     */
    Iterable<KnowledgeItem> findBySourceAgentId(String sourceAgentId);
    
    /**
     * Find knowledge items by domain area.
     * 
     * @param domainArea The domain area
     * @return List of knowledge items in the specified domain area
     */
    Iterable<KnowledgeItem> findByDomainArea(String domainArea);
    
    /**
     * Find knowledge items with confidence score greater than or equal to the specified value.
     * 
     * @param confidenceScore The minimum confidence score
     * @return List of knowledge items with confidence score greater than or equal to the specified value
     */
    Iterable<KnowledgeItem> findByConfidenceScoreGreaterThanEqual(Double confidenceScore);
}
