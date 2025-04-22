package ai.lumina.security.repository;

import ai.lumina.security.model.EthicalGovernancePolicy;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for managing EthicalGovernancePolicy entities.
 */
@Repository
public interface EthicalGovernancePolicyRepository extends JpaRepository<EthicalGovernancePolicy, Long> {

    /**
     * Find a policy by its ID.
     *
     * @param policyId The policy ID
     * @return The policy if found
     */
    Optional<EthicalGovernancePolicy> findByPolicyId(String policyId);

    /**
     * Find policies by name.
     *
     * @param name The policy name
     * @return List of matching policies
     */
    List<EthicalGovernancePolicy> findByNameContaining(String name);

    /**
     * Find policies by ethical principle.
     *
     * @param principle The ethical principle
     * @return List of matching policies
     */
    List<EthicalGovernancePolicy> findByPrinciple(EthicalGovernancePolicy.EthicalPrinciple principle);

    /**
     * Find policies by application domain.
     *
     * @param domain The application domain
     * @return List of matching policies
     */
    List<EthicalGovernancePolicy> findByDomain(EthicalGovernancePolicy.ApplicationDomain domain);

    /**
     * Find policies by human oversight level.
     *
     * @param humanOversightLevel The human oversight level
     * @return List of matching policies
     */
    List<EthicalGovernancePolicy> findByHumanOversightLevel(EthicalGovernancePolicy.HumanOversightLevel humanOversightLevel);

    /**
     * Find all enabled policies.
     *
     * @return List of enabled policies
     */
    List<EthicalGovernancePolicy> findByEnabledTrue();

    /**
     * Find policies that contain a specific fairness rule.
     *
     * @param fairnessRule The fairness rule
     * @return List of matching policies
     */
    @Query("SELECT p FROM EthicalGovernancePolicy p JOIN p.fairnessRules r WHERE r = :fairnessRule")
    List<EthicalGovernancePolicy> findByFairnessRule(String fairnessRule);

    /**
     * Find policies that contain a specific explainability rule.
     *
     * @param explainabilityRule The explainability rule
     * @return List of matching policies
     */
    @Query("SELECT p FROM EthicalGovernancePolicy p JOIN p.explainabilityRules r WHERE r = :explainabilityRule")
    List<EthicalGovernancePolicy> findByExplainabilityRule(String explainabilityRule);

    /**
     * Find policies by principle and domain.
     *
     * @param principle The ethical principle
     * @param domain The application domain
     * @return List of matching policies
     */
    List<EthicalGovernancePolicy> findByPrincipleAndDomain(
            EthicalGovernancePolicy.EthicalPrinciple principle,
            EthicalGovernancePolicy.ApplicationDomain domain);
}
