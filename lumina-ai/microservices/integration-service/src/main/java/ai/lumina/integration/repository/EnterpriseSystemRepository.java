package ai.lumina.integration.repository;

import ai.lumina.integration.model.EnterpriseSystem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository for managing EnterpriseSystem entities.
 */
@Repository
public interface EnterpriseSystemRepository extends JpaRepository<EnterpriseSystem, String> {

    /**
     * Find all enterprise systems of a specific type.
     *
     * @param systemType The type of system to find
     * @return List of enterprise systems
     */
    List<EnterpriseSystem> findBySystemType(String systemType);

    /**
     * Find all enabled enterprise systems.
     *
     * @return List of enabled enterprise systems
     */
    List<EnterpriseSystem> findByEnabledTrue();

    /**
     * Find all enabled enterprise systems of a specific type.
     *
     * @param systemType The type of system to find
     * @return List of enabled enterprise systems
     */
    List<EnterpriseSystem> findBySystemTypeAndEnabledTrue(String systemType);

    /**
     * Find enterprise systems with a specific metadata key-value pair.
     *
     * @param metaKey The metadata key
     * @param metaValue The metadata value
     * @return List of matching enterprise systems
     */
    @Query("SELECT es FROM EnterpriseSystem es JOIN es.metadata m WHERE KEY(m) = ?1 AND VALUE(m) = ?2")
    List<EnterpriseSystem> findByMetadata(String metaKey, String metaValue);
}
