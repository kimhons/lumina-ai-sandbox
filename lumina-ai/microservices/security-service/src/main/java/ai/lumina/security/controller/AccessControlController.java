package ai.lumina.security.controller;

import ai.lumina.security.model.AccessControlPolicy;
import ai.lumina.security.service.AccessControlService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST controller for access control operations.
 */
@RestController
@RequestMapping("/api/security/access-control")
@RequiredArgsConstructor
@Slf4j
public class AccessControlController {

    private final AccessControlService accessControlService;

    /**
     * Create a new access control policy.
     *
     * @param policy The policy to create
     * @return The created policy
     */
    @PostMapping("/policies")
    public ResponseEntity<AccessControlPolicy> createPolicy(@RequestBody AccessControlPolicy policy) {
        log.info("REST request to create access control policy: {}", policy.getName());
        AccessControlPolicy createdPolicy = accessControlService.createPolicy(policy);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdPolicy);
    }

    /**
     * Update an existing access control policy.
     *
     * @param id The policy ID
     * @param policy The updated policy
     * @return The updated policy
     */
    @PutMapping("/policies/{id}")
    public ResponseEntity<AccessControlPolicy> updatePolicy(
            @PathVariable Long id,
            @RequestBody AccessControlPolicy policy) {
        log.info("REST request to update access control policy with ID: {}", id);
        return accessControlService.updatePolicy(id, policy)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Delete an access control policy.
     *
     * @param id The policy ID
     * @return No content response
     */
    @DeleteMapping("/policies/{id}")
    public ResponseEntity<Void> deletePolicy(@PathVariable Long id) {
        log.info("REST request to delete access control policy with ID: {}", id);
        accessControlService.deletePolicy(id);
        return ResponseEntity.noContent().build();
    }

    /**
     * Get an access control policy by ID.
     *
     * @param id The policy ID
     * @return The policy if found
     */
    @GetMapping("/policies/{id}")
    public ResponseEntity<AccessControlPolicy> getPolicy(@PathVariable Long id) {
        log.info("REST request to get access control policy with ID: {}", id);
        return accessControlService.getPolicyById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get all access control policies.
     *
     * @return List of all policies
     */
    @GetMapping("/policies")
    public ResponseEntity<List<AccessControlPolicy>> getAllPolicies() {
        log.info("REST request to get all access control policies");
        List<AccessControlPolicy> policies = accessControlService.getAllPolicies();
        return ResponseEntity.ok(policies);
    }

    /**
     * Get policies by type.
     *
     * @param policyType The policy type
     * @return List of matching policies
     */
    @GetMapping("/policies/by-type/{policyType}")
    public ResponseEntity<List<AccessControlPolicy>> getPoliciesByType(
            @PathVariable AccessControlPolicy.PolicyType policyType) {
        log.info("REST request to get access control policies by type: {}", policyType);
        List<AccessControlPolicy> policies = accessControlService.getPoliciesByType(policyType);
        return ResponseEntity.ok(policies);
    }

    /**
     * Check if a user has access to a resource.
     *
     * @param userId The user ID
     * @param resource The resource
     * @param action The action
     * @param context The context
     * @return True if access is granted, false otherwise
     */
    @GetMapping("/check-access")
    public ResponseEntity<Boolean> checkAccess(
            @RequestParam String userId,
            @RequestParam String resource,
            @RequestParam String action,
            @RequestParam(required = false) String context) {
        log.info("REST request to check access for user {} to resource {} for action {}", 
                userId, resource, action);
        boolean hasAccess = accessControlService.hasAccess(userId, resource, action, context);
        return ResponseEntity.ok(hasAccess);
    }
}
