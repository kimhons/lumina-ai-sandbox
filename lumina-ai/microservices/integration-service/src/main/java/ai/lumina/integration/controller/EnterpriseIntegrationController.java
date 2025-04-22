package ai.lumina.integration.controller;

import ai.lumina.integration.dto.EnterpriseSystemDto;
import ai.lumina.integration.dto.IntegrationRequestDto;
import ai.lumina.integration.dto.IntegrationResponseDto;
import ai.lumina.integration.service.EnterpriseIntegrationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST controller for enterprise integration operations.
 */
@RestController
@RequestMapping("/api/v1/integration")
@RequiredArgsConstructor
@Slf4j
public class EnterpriseIntegrationController {

    private final EnterpriseIntegrationService integrationService;

    /**
     * Register a new enterprise system.
     *
     * @param dto The enterprise system data
     * @return The registered system
     */
    @PostMapping("/systems")
    public ResponseEntity<EnterpriseSystemDto> registerSystem(@RequestBody EnterpriseSystemDto dto) {
        log.info("REST request to register enterprise system: {}", dto.getSystemId());
        EnterpriseSystemDto result = integrationService.registerSystem(dto);
        return ResponseEntity.status(HttpStatus.CREATED).body(result);
    }

    /**
     * Update an existing enterprise system.
     *
     * @param systemId The ID of the system to update
     * @param dto The updated system data
     * @return The updated system
     */
    @PutMapping("/systems/{systemId}")
    public ResponseEntity<EnterpriseSystemDto> updateSystem(
            @PathVariable String systemId,
            @RequestBody EnterpriseSystemDto dto) {
        log.info("REST request to update enterprise system: {}", systemId);
        EnterpriseSystemDto result = integrationService.updateSystem(systemId, dto);
        return ResponseEntity.ok(result);
    }

    /**
     * Get an enterprise system by ID.
     *
     * @param systemId The ID of the system
     * @return The enterprise system
     */
    @GetMapping("/systems/{systemId}")
    public ResponseEntity<EnterpriseSystemDto> getSystem(@PathVariable String systemId) {
        log.info("REST request to get enterprise system: {}", systemId);
        EnterpriseSystemDto result = integrationService.getSystem(systemId);
        return ResponseEntity.ok(result);
    }

    /**
     * List all enterprise systems.
     *
     * @param systemType Optional system type filter
     * @param enabledOnly Whether to return only enabled systems
     * @return List of enterprise systems
     */
    @GetMapping("/systems")
    public ResponseEntity<List<EnterpriseSystemDto>> listSystems(
            @RequestParam(required = false) String systemType,
            @RequestParam(defaultValue = "false") boolean enabledOnly) {
        log.info("REST request to list enterprise systems. Type: {}, EnabledOnly: {}", systemType, enabledOnly);
        List<EnterpriseSystemDto> result = integrationService.listSystems(systemType, enabledOnly);
        return ResponseEntity.ok(result);
    }

    /**
     * Delete an enterprise system.
     *
     * @param systemId The ID of the system to delete
     * @return No content response
     */
    @DeleteMapping("/systems/{systemId}")
    public ResponseEntity<Void> deleteSystem(@PathVariable String systemId) {
        log.info("REST request to delete enterprise system: {}", systemId);
        integrationService.deleteSystem(systemId);
        return ResponseEntity.noContent().build();
    }

    /**
     * Execute an integration operation.
     *
     * @param request The integration request
     * @return The integration response
     */
    @PostMapping("/execute")
    public ResponseEntity<IntegrationResponseDto> executeOperation(@RequestBody IntegrationRequestDto request) {
        log.info("REST request to execute integration operation. SystemId: {}, Operation: {}", 
                request.getSystemId(), request.getOperation());
        IntegrationResponseDto result = integrationService.executeOperation(request);
        return ResponseEntity.ok(result);
    }

    /**
     * Store credentials for an enterprise system.
     *
     * @param systemId The ID of the system
     * @param credentials The credentials to store
     * @return Success response
     */
    @PostMapping("/systems/{systemId}/credentials")
    public ResponseEntity<Map<String, Boolean>> storeCredentials(
            @PathVariable String systemId,
            @RequestBody Map<String, String> credentials) {
        log.info("REST request to store credentials for system: {}", systemId);
        boolean success = integrationService.storeCredentials(systemId, credentials);
        return ResponseEntity.ok(Map.of("success", success));
    }
}
