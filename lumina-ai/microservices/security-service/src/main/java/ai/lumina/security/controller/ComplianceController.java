package ai.lumina.security.controller;

import ai.lumina.security.model.ComplianceRequirement;
import ai.lumina.security.service.ComplianceService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST controller for compliance operations.
 */
@RestController
@RequestMapping("/api/security/compliance")
@RequiredArgsConstructor
@Slf4j
public class ComplianceController {

    private final ComplianceService complianceService;

    /**
     * Create a new compliance requirement.
     *
     * @param requirement The requirement to create
     * @return The created requirement
     */
    @PostMapping("/requirements")
    public ResponseEntity<ComplianceRequirement> createRequirement(@RequestBody ComplianceRequirement requirement) {
        log.info("REST request to create compliance requirement: {}", requirement.getName());
        ComplianceRequirement createdRequirement = complianceService.createRequirement(requirement);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdRequirement);
    }

    /**
     * Update an existing compliance requirement.
     *
     * @param id The requirement ID
     * @param requirement The updated requirement
     * @return The updated requirement
     */
    @PutMapping("/requirements/{id}")
    public ResponseEntity<ComplianceRequirement> updateRequirement(
            @PathVariable Long id,
            @RequestBody ComplianceRequirement requirement) {
        log.info("REST request to update compliance requirement with ID: {}", id);
        return complianceService.updateRequirement(id, requirement)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Delete a compliance requirement.
     *
     * @param id The requirement ID
     * @return No content response
     */
    @DeleteMapping("/requirements/{id}")
    public ResponseEntity<Void> deleteRequirement(@PathVariable Long id) {
        log.info("REST request to delete compliance requirement with ID: {}", id);
        complianceService.deleteRequirement(id);
        return ResponseEntity.noContent().build();
    }

    /**
     * Get a compliance requirement by ID.
     *
     * @param id The requirement ID
     * @return The requirement if found
     */
    @GetMapping("/requirements/{id}")
    public ResponseEntity<ComplianceRequirement> getRequirement(@PathVariable Long id) {
        log.info("REST request to get compliance requirement with ID: {}", id);
        return complianceService.getRequirementById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Get all compliance requirements.
     *
     * @return List of all requirements
     */
    @GetMapping("/requirements")
    public ResponseEntity<List<ComplianceRequirement>> getAllRequirements() {
        log.info("REST request to get all compliance requirements");
        List<ComplianceRequirement> requirements = complianceService.getAllRequirements();
        return ResponseEntity.ok(requirements);
    }

    /**
     * Get requirements by framework type.
     *
     * @param frameworkType The framework type
     * @return List of matching requirements
     */
    @GetMapping("/requirements/by-framework/{frameworkType}")
    public ResponseEntity<List<ComplianceRequirement>> getRequirementsByFrameworkType(
            @PathVariable ComplianceRequirement.FrameworkType frameworkType) {
        log.info("REST request to get compliance requirements by framework type: {}", frameworkType);
        List<ComplianceRequirement> requirements = complianceService.getRequirementsByFrameworkType(frameworkType);
        return ResponseEntity.ok(requirements);
    }

    /**
     * Get requirements by severity.
     *
     * @param severity The severity
     * @return List of matching requirements
     */
    @GetMapping("/requirements/by-severity/{severity}")
    public ResponseEntity<List<ComplianceRequirement>> getRequirementsBySeverity(
            @PathVariable ComplianceRequirement.RequirementSeverity severity) {
        log.info("REST request to get compliance requirements by severity: {}", severity);
        List<ComplianceRequirement> requirements = complianceService.getRequirementsBySeverity(severity);
        return ResponseEntity.ok(requirements);
    }

    /**
     * Generate a compliance report for a specific framework.
     *
     * @param frameworkType The framework type
     * @return A compliance report
     */
    @GetMapping("/reports/{frameworkType}")
    public ResponseEntity<String> generateComplianceReport(
            @PathVariable ComplianceRequirement.FrameworkType frameworkType) {
        log.info("REST request to generate compliance report for framework: {}", frameworkType);
        String report = complianceService.generateComplianceReport(frameworkType);
        return ResponseEntity.ok(report);
    }

    /**
     * Check compliance for a specific requirement.
     *
     * @param requirementId The requirement ID
     * @return True if compliant, false otherwise
     */
    @GetMapping("/check/{requirementId}")
    public ResponseEntity<Boolean> checkCompliance(@PathVariable String requirementId) {
        log.info("REST request to check compliance for requirement: {}", requirementId);
        boolean isCompliant = complianceService.checkCompliance(requirementId);
        return ResponseEntity.ok(isCompliant);
    }
}
