package ai.lumina.security.repository;

import ai.lumina.security.model.ComplianceRequirement;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for managing ComplianceRequirement entities.
 */
@Repository
public interface ComplianceRequirementRepository extends JpaRepository<ComplianceRequirement, Long> {

    /**
     * Find a requirement by its ID.
     *
     * @param requirementId The requirement ID
     * @return The requirement if found
     */
    Optional<ComplianceRequirement> findByRequirementId(String requirementId);

    /**
     * Find requirements by name.
     *
     * @param name The requirement name
     * @return List of matching requirements
     */
    List<ComplianceRequirement> findByNameContaining(String name);

    /**
     * Find requirements by framework type.
     *
     * @param frameworkType The framework type
     * @return List of matching requirements
     */
    List<ComplianceRequirement> findByFrameworkType(ComplianceRequirement.FrameworkType frameworkType);

    /**
     * Find requirements by framework version.
     *
     * @param frameworkVersion The framework version
     * @return List of matching requirements
     */
    List<ComplianceRequirement> findByFrameworkVersion(String frameworkVersion);

    /**
     * Find requirements by category.
     *
     * @param category The category
     * @return List of matching requirements
     */
    List<ComplianceRequirement> findByCategory(String category);

    /**
     * Find requirements by severity.
     *
     * @param severity The severity
     * @return List of matching requirements
     */
    List<ComplianceRequirement> findBySeverity(ComplianceRequirement.RequirementSeverity severity);

    /**
     * Find all enabled requirements.
     *
     * @return List of enabled requirements
     */
    List<ComplianceRequirement> findByEnabledTrue();

    /**
     * Find requirements by framework type and severity.
     *
     * @param frameworkType The framework type
     * @param severity The severity
     * @return List of matching requirements
     */
    List<ComplianceRequirement> findByFrameworkTypeAndSeverity(
            ComplianceRequirement.FrameworkType frameworkType,
            ComplianceRequirement.RequirementSeverity severity);

    /**
     * Find requirements that contain a specific compliance check.
     *
     * @param checkDescription The check description
     * @return List of matching requirements
     */
    @Query("SELECT r FROM ComplianceRequirement r JOIN r.complianceChecks c WHERE c = :checkDescription")
    List<ComplianceRequirement> findByComplianceCheck(String checkDescription);

    /**
     * Find requirements that require a specific evidence type.
     *
     * @param evidenceType The evidence type
     * @return List of matching requirements
     */
    @Query("SELECT r FROM ComplianceRequirement r JOIN r.evidenceTypes e WHERE e = :evidenceType")
    List<ComplianceRequirement> findByEvidenceType(String evidenceType);
}
