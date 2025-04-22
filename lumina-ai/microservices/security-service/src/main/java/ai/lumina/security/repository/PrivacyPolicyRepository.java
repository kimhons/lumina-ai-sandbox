package ai.lumina.security.repository;

import ai.lumina.security.model.PrivacyPolicy;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for managing PrivacyPolicy entities.
 */
@Repository
public interface PrivacyPolicyRepository extends JpaRepository<PrivacyPolicy, Long> {

    /**
     * Find a policy by its ID.
     *
     * @param policyId The policy ID
     * @return The policy if found
     */
    Optional<PrivacyPolicy> findByPolicyId(String policyId);

    /**
     * Find policies by name.
     *
     * @param name The policy name
     * @return List of matching policies
     */
    List<PrivacyPolicy> findByNameContaining(String name);

    /**
     * Find policies by data category.
     *
     * @param dataCategory The data category
     * @return List of matching policies
     */
    List<PrivacyPolicy> findByDataCategory(PrivacyPolicy.DataCategory dataCategory);

    /**
     * Find policies by retention period.
     *
     * @param retentionPeriodDays The retention period in days
     * @return List of matching policies
     */
    List<PrivacyPolicy> findByRetentionPeriodDays(Integer retentionPeriodDays);

    /**
     * Find policies that require consent.
     *
     * @return List of matching policies
     */
    List<PrivacyPolicy> findByRequiresConsentTrue();

    /**
     * Find policies that allow data sharing.
     *
     * @return List of matching policies
     */
    List<PrivacyPolicy> findByAllowsDataSharingTrue();

    /**
     * Find policies by privacy level.
     *
     * @param privacyLevel The privacy level
     * @return List of matching policies
     */
    List<PrivacyPolicy> findByPrivacyLevel(PrivacyPolicy.PrivacyLevel privacyLevel);

    /**
     * Find all enabled policies.
     *
     * @return List of enabled policies
     */
    List<PrivacyPolicy> findByEnabledTrue();

    /**
     * Find policies that contain a specific minimization rule.
     *
     * @param minimizationRule The minimization rule
     * @return List of matching policies
     */
    @Query("SELECT p FROM PrivacyPolicy p JOIN p.minimizationRules r WHERE r = :minimizationRule")
    List<PrivacyPolicy> findByMinimizationRule(String minimizationRule);

    /**
     * Find policies that contain a specific anonymization rule.
     *
     * @param anonymizationRule The anonymization rule
     * @return List of matching policies
     */
    @Query("SELECT p FROM PrivacyPolicy p JOIN p.anonymizationRules r WHERE r = :anonymizationRule")
    List<PrivacyPolicy> findByAnonymizationRule(String anonymizationRule);
}
