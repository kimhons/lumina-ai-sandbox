package ai.lumina.collaboration.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import ai.lumina.collaboration.model.SharedContext;

/**
 * Repository for shared context operations.
 */
@Repository
public interface SharedContextRepository extends JpaRepository<SharedContext, String> {
    
    /**
     * Find contexts by name containing the given string (case insensitive).
     * 
     * @param name The name to search for
     * @return List of matching contexts
     */
    List<SharedContext> findByNameContainingIgnoreCase(String name);
    
    /**
     * Find contexts by context type and name containing the given string (case insensitive).
     * 
     * @param contextType The context type
     * @param name The name to search for
     * @return List of matching contexts
     */
    List<SharedContext> findByContextTypeAndNameContainingIgnoreCase(String contextType, String name);
    
    /**
     * Find contexts by owner ID.
     * 
     * @param ownerId The owner ID
     * @return List of matching contexts
     */
    List<SharedContext> findByOwnerId(String ownerId);
    
    /**
     * Find contexts by context type.
     * 
     * @param contextType The context type
     * @return List of matching contexts
     */
    List<SharedContext> findByContextType(String contextType);
}
