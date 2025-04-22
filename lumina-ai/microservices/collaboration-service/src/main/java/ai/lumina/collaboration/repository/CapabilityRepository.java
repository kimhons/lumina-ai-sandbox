package ai.lumina.collaboration.repository;

import ai.lumina.collaboration.model.Capability;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository interface for Capability entity operations.
 */
@Repository
public interface CapabilityRepository extends JpaRepository<Capability, String> {

    /**
     * Find capability by name.
     *
     * @param name The capability name to search for
     * @return The capability with the specified name
     */
    Capability findByName(String name);

    /**
     * Find capabilities by category.
     *
     * @param category The category to search for
     * @return List of capabilities in the specified category
     */
    List<Capability> findByCategory(String category);

    /**
     * Find capabilities by complexity level.
     *
     * @param complexityLevel The complexity level to search for
     * @return List of capabilities with the specified complexity level
     */
    List<Capability> findByComplexityLevel(int complexityLevel);

    /**
     * Find capabilities by complexity level less than or equal to a threshold.
     *
     * @param maxComplexity The maximum complexity level
     * @return List of capabilities with complexity level less than or equal to the threshold
     */
    List<Capability> findByComplexityLevelLessThanEqual(int maxComplexity);

    /**
     * Find core capabilities.
     *
     * @return List of core capabilities
     */
    List<Capability> findByIsCore(boolean isCore);

    /**
     * Find capabilities by category and complexity level.
     *
     * @param category The category to search for
     * @param complexityLevel The complexity level to search for
     * @return List of capabilities in the specified category with the specified complexity level
     */
    List<Capability> findByCategoryAndComplexityLevel(String category, int complexityLevel);

    /**
     * Find capabilities by category ordered by complexity level.
     *
     * @param category The category to search for
     * @return List of capabilities in the specified category ordered by complexity level
     */
    @Query("SELECT c FROM Capability c WHERE c.category = :category ORDER BY c.complexityLevel")
    List<Capability> findByCategoryOrderedByComplexity(@Param("category") String category);

    /**
     * Find capabilities by name containing a substring.
     *
     * @param nameSubstring The substring to search for in capability names
     * @return List of capabilities with names containing the specified substring
     */
    List<Capability> findByNameContaining(String nameSubstring);
}
