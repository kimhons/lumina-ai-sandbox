package ai.lumina.security.controller;

import ai.lumina.security.model.PrivacyPolicy;
import ai.lumina.security.service.PrivacyService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST controller for privacy operations.
 */
@RestController
@RequestMapping("/api/security/privacy")
@RequiredArgsConstructor
@Slf4j
public class PrivacyController {

    private final PrivacyService privacyService;

    /**
     * Create a new privacy policy.
     *
     * @param policy The policy to create
     * @return The created policy
     */
    @PostMapping("/policies")
    public ResponseEntity<PrivacyPolicy> createPolicy(@RequestBody PrivacyPolicy policy) {
        log.info("REST request to create privacy policy: {}", policy.getName());
        PrivacyPolicy createdPolicy = privacyService.createPolicy(policy);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdPolicy);
    }

    /**
     * Update an existing privacy policy.
     *
     * @param id The policy ID
     * @param policy The updated policy
     * @return The updated policy
     */
    @PutMapping("/policies/{id}")
    public ResponseEntity<PrivacyPolicy> updatePolicy(
            @PathVariable Long id,
            @RequestBody PrivacyPolicy policy) {
        log.info("REST request to update privacy policy with ID: {}", id);
        return privacyService.updatePolicy(id, policy)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Delete a privacy policy.
     *
     * @param id The policy ID
     * @return No content response
     */
    @DeleteMapping("/policies/{id}")
    public ResponseEntity<Void> deletePolicy(@PathVariable Long id) {
        log.info("REST request to delete privacy policy with ID: {}", id);
        privacyService.deletePolicy(id);
        return ResponseEntity.noContent().build();
    }

    /**
     * Get a privacy policy by ID.
     *
     * @param id The policy ID
     * @return The policy if found
     */
    @GetMapping("/policies/{id}")
    public ResponseEntity<PrivacyPolicy> getPolicy(@PathVariable Long id) {
        log.info("REST request to get privacy policy with ID: {}", id);
        return privacyService.getPolicyById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get all privacy policies.
     *
     * @return List of all policies
     */
    @GetMapping("/policies")
    public ResponseEntity<List<PrivacyPolicy>> getAllPolicies() {
        log.info("REST request to get all privacy policies");
        List<PrivacyPolicy> policies = privacyService.getAllPolicies();
        return ResponseEntity.ok(policies);
    }

    /**
     * Get policies by data category.
     *
     * @param dataCategory The data category
     * @return List of matching policies
     */
    @GetMapping("/policies/by-category/{dataCategory}")
    public ResponseEntity<List<PrivacyPolicy>> getPoliciesByDataCategory(
            @PathVariable PrivacyPolicy.DataCategory dataCategory) {
        log.info("REST request to get privacy policies by data category: {}", dataCategory);
        List<PrivacyPolicy> policies = privacyService.getPoliciesByDataCategory(dataCategory);
        return ResponseEntity.ok(policies);
    }

    /**
     * Get policies by privacy level.
     *
     * @param privacyLevel The privacy level
     * @return List of matching policies
     */
    @GetMapping("/policies/by-level/{privacyLevel}")
    public ResponseEntity<List<PrivacyPolicy>> getPoliciesByPrivacyLevel(
            @PathVariable PrivacyPolicy.PrivacyLevel privacyLevel) {
        log.info("REST request to get privacy policies by privacy level: {}", privacyLevel);
        List<PrivacyPolicy> policies = privacyService.getPoliciesByPrivacyLevel(privacyLevel);
        return ResponseEntity.ok(policies);
    }

    /**
     * Apply data minimization to a data object.
     *
     * @param data The data to minimize
     * @param dataCategory The data category
     * @return The minimized data
     */
    @PostMapping("/minimize")
    public ResponseEntity<String> applyDataMinimization(
            @RequestParam String data,
            @RequestParam PrivacyPolicy.DataCategory dataCategory) {
        log.info("REST request to apply data minimization for category: {}", dataCategory);
        String minimizedData = privacyService.applyDataMinimization(data, dataCategory);
        return ResponseEntity.ok(minimizedData);
    }

    /**
     * Apply anonymization to a data object.
     *
     * @param data The data to anonymize
     * @param dataCategory The data category
     * @return The anonymized data
     */
    @PostMapping("/anonymize")
    public ResponseEntity<String> applyAnonymization(
            @RequestParam String data,
            @RequestParam PrivacyPolicy.DataCategory dataCategory) {
        log.info("REST request to apply anonymization for category: {}", dataCategory);
        String anonymizedData = privacyService.applyAnonymization(data, dataCategory);
        return ResponseEntity.ok(anonymizedData);
    }

    /**
     * Apply pseudonymization to a data object.
     *
     * @param data The data to pseudonymize
     * @param dataCategory The data category
     * @return The pseudonymized data
     */
    @PostMapping("/pseudonymize")
    public ResponseEntity<String> applyPseudonymization(
            @RequestParam String data,
            @RequestParam PrivacyPolicy.DataCategory dataCategory) {
        log.info("REST request to apply pseudonymization for category: {}", dataCategory);
        String pseudonymizedData = privacyService.applyPseudonymization(data, dataCategory);
        return ResponseEntity.ok(pseudonymizedData);
    }

    /**
     * Apply differential privacy to a query.
     *
     * @param query The query
     * @param epsilon The privacy parameter
     * @return The privacy-preserving query result
     */
    @PostMapping("/differential-privacy")
    public ResponseEntity<String> applyDifferentialPrivacy(
            @RequestParam String query,
            @RequestParam double epsilon) {
        log.info("REST request to apply differential privacy with epsilon: {}", epsilon);
        String result = privacyService.applyDifferentialPrivacy(query, epsilon);
        return ResponseEntity.ok(result);
    }
}
