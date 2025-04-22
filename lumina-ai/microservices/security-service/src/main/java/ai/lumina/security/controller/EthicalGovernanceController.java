package ai.lumina.security.controller;

import ai.lumina.security.model.EthicalGovernancePolicy;
import ai.lumina.security.service.EthicalGovernanceService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST controller for ethical governance operations.
 */
@RestController
@RequestMapping("/api/security/ethical")
@RequiredArgsConstructor
@Slf4j
public class EthicalGovernanceController {

    private final EthicalGovernanceService ethicalGovernanceService;

    /**
     * Create a new ethical governance policy.
     *
     * @param policy The policy to create
     * @return The created policy
     */
    @PostMapping("/policies")
    public ResponseEntity<EthicalGovernancePolicy> createPolicy(@RequestBody EthicalGovernancePolicy policy) {
        log.info("REST request to create ethical governance policy: {}", policy.getName());
        EthicalGovernancePolicy createdPolicy = ethicalGovernanceService.createPolicy(policy);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdPolicy);
    }

    /**
     * Update an existing ethical governance policy.
     *
     * @param id The policy ID
     * @param policy The updated policy
     * @return The updated policy
     */
    @PutMapping("/policies/{id}")
    public ResponseEntity<EthicalGovernancePolicy> updatePolicy(
            @PathVariable Long id,
            @RequestBody EthicalGovernancePolicy policy) {
        log.info("REST request to update ethical governance policy with ID: {}", id);
        return ethicalGovernanceService.updatePolicy(id, policy)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Delete an ethical governance policy.
     *
     * @param id The policy ID
     * @return No content response
     */
    @DeleteMapping("/policies/{id}")
    public ResponseEntity<Void> deletePolicy(@PathVariable Long id) {
        log.info("REST request to delete ethical governance policy with ID: {}", id);
        ethicalGovernanceService.deletePolicy(id);
        return ResponseEntity.noContent().build();
    }

    /**
     * Get an ethical governance policy by ID.
     *
     * @param id The policy ID
     * @return The policy if found
     */
    @GetMapping("/policies/{id}")
    public ResponseEntity<EthicalGovernancePolicy> getPolicy(@PathVariable Long id) {
        log.info("REST request to get ethical governance policy with ID: {}", id);
        return ethicalGovernanceService.getPolicyById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get all ethical governance policies.
     *
     * @return List of all policies
     */
    @GetMapping("/policies")
    public ResponseEntity<List<EthicalGovernancePolicy>> getAllPolicies() {
        log.info("REST request to get all ethical governance policies");
        List<EthicalGovernancePolicy> policies = ethicalGovernanceService.getAllPolicies();
        return ResponseEntity.ok(policies);
    }

    /**
     * Get policies by ethical principle.
     *
     * @param principle The ethical principle
     * @return List of matching policies
     */
    @GetMapping("/policies/by-principle/{principle}")
    public ResponseEntity<List<EthicalGovernancePolicy>> getPoliciesByPrinciple(
            @PathVariable EthicalGovernancePolicy.EthicalPrinciple principle) {
        log.info("REST request to get ethical governance policies by principle: {}", principle);
        List<EthicalGovernancePolicy> policies = ethicalGovernanceService.getPoliciesByPrinciple(principle);
        return ResponseEntity.ok(policies);
    }

    /**
     * Get policies by application domain.
     *
     * @param domain The application domain
     * @return List of matching policies
     */
    @GetMapping("/policies/by-domain/{domain}")
    public ResponseEntity<List<EthicalGovernancePolicy>> getPoliciesByDomain(
            @PathVariable EthicalGovernancePolicy.ApplicationDomain domain) {
        log.info("REST request to get ethical governance policies by domain: {}", domain);
        List<EthicalGovernancePolicy> policies = ethicalGovernanceService.getPoliciesByDomain(domain);
        return ResponseEntity.ok(policies);
    }

    /**
     * Detect bias in a model or dataset.
     *
     * @param data The data to analyze
     * @param sensitiveAttributes The sensitive attributes to check for bias
     * @return A bias assessment report
     */
    @PostMapping("/detect-bias")
    public ResponseEntity<Map<String, Double>> detectBias(
            @RequestParam String data,
            @RequestParam List<String> sensitiveAttributes) {
        log.info("REST request to detect bias for sensitive attributes: {}", sensitiveAttributes);
        Map<String, Double> biasReport = ethicalGovernanceService.detectBias(data, sensitiveAttributes);
        return ResponseEntity.ok(biasReport);
    }

    /**
     * Generate explanations for an AI decision.
     *
     * @param decision The decision to explain
     * @param model The model that made the decision
     * @return An explanation of the decision
     */
    @PostMapping("/explain")
    public ResponseEntity<String> generateExplanation(
            @RequestParam String decision,
            @RequestParam String model) {
        log.info("REST request to generate explanation for decision from model: {}", model);
        String explanation = ethicalGovernanceService.generateExplanation(decision, model);
        return ResponseEntity.ok(explanation);
    }

    /**
     * Assess the fairness of an AI system.
     *
     * @param systemId The AI system ID
     * @return A fairness assessment report
     */
    @GetMapping("/assess-fairness/{systemId}")
    public ResponseEntity<Map<String, Object>> assessFairness(@PathVariable String systemId) {
        log.info("REST request to assess fairness for AI system: {}", systemId);
        Map<String, Object> fairnessReport = ethicalGovernanceService.assessFairness(systemId);
        return ResponseEntity.ok(fairnessReport);
    }

    /**
     * Determine the appropriate human oversight level for a given AI task.
     *
     * @param taskDescription The task description
     * @param riskLevel The risk level
     * @return The recommended human oversight level
     */
    @PostMapping("/determine-oversight")
    public ResponseEntity<EthicalGovernancePolicy.HumanOversightLevel> determineHumanOversightLevel(
            @RequestParam String taskDescription,
            @RequestParam String riskLevel) {
        log.info("REST request to determine human oversight level for task with risk level: {}", riskLevel);
        EthicalGovernancePolicy.HumanOversightLevel oversightLevel = 
                ethicalGovernanceService.determineHumanOversightLevel(taskDescription, riskLevel);
        return ResponseEntity.ok(oversightLevel);
    }
}
