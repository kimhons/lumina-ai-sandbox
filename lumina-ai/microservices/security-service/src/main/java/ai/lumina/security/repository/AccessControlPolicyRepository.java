package ai.lumina.security.repository;

import ai.lumina.security.model.AccessControlPolicy;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for managing AccessControlPolicy entities.
 */
@Repository
public interface AccessControlPolicyRepository extends JpaRepository<AccessControlPolicy, Long> {

    /**
     * Find a policy by its name.
     *
     * @param name The policy name
     * @return The policy if found
     */
    Optional<AccessControlPolicy> findByName(String name);

    /**
     * Find all policies of a specific type.
     *
     * @param policyType The policy type
     * @return List of matching policies
     */
    List<AccessControlPolicy> findByPolicyType(AccessControlPolicy.PolicyType policyType);

    /**
     * Find all enabled policies.
     *
     * @return List of enabled policies
     */
    List<AccessControlPolicy> findByEnabledTrue();

    /**
     * Find policies that match a resource pattern.
     *
     * @param resourcePattern The resource pattern
     * @return List of matching policies
     */
    List<AccessControlPolicy> findByResourcePatternLike(String resourcePattern);

    /**
     * Find policies that match an action pattern.
     *
     * @param actionPattern The action pattern
     * @return List of matching policies
     */
    List<AccessControlPolicy> findByActionPatternLike(String actionPattern);

    /**
     * Find policies that contain a specific role constraint.
     *
     * @param roleConstraint The role constraint
     * @return List of matching policies
     */
    @Query("SELECT p FROM AccessControlPolicy p JOIN p.roleConstraints r WHERE r = :roleConstraint")
    List<AccessControlPolicy> findByRoleConstraint(String roleConstraint);

    /**
     * Find policies that contain a specific attribute constraint.
     *
     * @param attributeConstraint The attribute constraint
     * @return List of matching policies
     */
    @Query("SELECT p FROM AccessControlPolicy p JOIN p.attributeConstraints a WHERE a = :attributeConstraint")
    List<AccessControlPolicy> findByAttributeConstraint(String attributeConstraint);

    /**
     * Find policies that contain a specific context constraint.
     *
     * @param contextConstraint The context constraint
     * @return List of matching policies
     */
    @Query("SELECT p FROM AccessControlPolicy p JOIN p.contextConstraints c WHERE c = :contextConstraint")
    List<AccessControlPolicy> findByContextConstraint(String contextConstraint);
}
