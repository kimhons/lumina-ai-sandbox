package ai.lumina.integration.service;

import ai.lumina.integration.dto.EnterpriseSystemDto;
import ai.lumina.integration.dto.IntegrationRequestDto;
import ai.lumina.integration.dto.IntegrationResponseDto;
import ai.lumina.integration.model.EnterpriseSystem;
import ai.lumina.integration.repository.EnterpriseSystemRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import javax.transaction.Transactional;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Service for managing enterprise system integrations.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class EnterpriseIntegrationService {

    private final EnterpriseSystemRepository enterpriseSystemRepository;
    private final IntegrationAdapterService adapterService;
    private final SecurityService securityService;
    private final MonitoringService monitoringService;

    /**
     * Register a new enterprise system.
     *
     * @param dto The enterprise system data
     * @return The registered system
     */
    @Transactional
    public EnterpriseSystemDto registerSystem(EnterpriseSystemDto dto) {
        log.info("Registering enterprise system: {}", dto.getSystemId());
        
        EnterpriseSystem system = convertToEntity(dto);
        system = enterpriseSystemRepository.save(system);
        
        return convertToDto(system);
    }

    /**
     * Update an existing enterprise system.
     *
     * @param systemId The ID of the system to update
     * @param dto The updated system data
     * @return The updated system
     */
    @Transactional
    public EnterpriseSystemDto updateSystem(String systemId, EnterpriseSystemDto dto) {
        log.info("Updating enterprise system: {}", systemId);
        
        EnterpriseSystem system = enterpriseSystemRepository.findById(systemId)
                .orElseThrow(() -> new RuntimeException("System not found: " + systemId));
        
        // Update fields
        system.setName(dto.getName());
        system.setDescription(dto.getDescription());
        system.setEnabled(dto.isEnabled());
        system.setConnectionParams(dto.getConnectionParams());
        system.setAuthParams(dto.getAuthParams());
        system.setTransformParams(dto.getTransformParams());
        system.setMetadata(dto.getMetadata());
        
        system = enterpriseSystemRepository.save(system);
        
        return convertToDto(system);
    }

    /**
     * Get an enterprise system by ID.
     *
     * @param systemId The ID of the system
     * @return The enterprise system
     */
    public EnterpriseSystemDto getSystem(String systemId) {
        log.info("Getting enterprise system: {}", systemId);
        
        EnterpriseSystem system = enterpriseSystemRepository.findById(systemId)
                .orElseThrow(() -> new RuntimeException("System not found: " + systemId));
        
        return convertToDto(system);
    }

    /**
     * List all enterprise systems.
     *
     * @param systemType Optional system type filter
     * @param enabledOnly Whether to return only enabled systems
     * @return List of enterprise systems
     */
    public List<EnterpriseSystemDto> listSystems(String systemType, boolean enabledOnly) {
        log.info("Listing enterprise systems. Type: {}, EnabledOnly: {}", systemType, enabledOnly);
        
        List<EnterpriseSystem> systems;
        
        if (systemType != null && enabledOnly) {
            systems = enterpriseSystemRepository.findBySystemTypeAndEnabledTrue(systemType);
        } else if (systemType != null) {
            systems = enterpriseSystemRepository.findBySystemType(systemType);
        } else if (enabledOnly) {
            systems = enterpriseSystemRepository.findByEnabledTrue();
        } else {
            systems = enterpriseSystemRepository.findAll();
        }
        
        return systems.stream()
                .map(this::convertToDto)
                .collect(Collectors.toList());
    }

    /**
     * Delete an enterprise system.
     *
     * @param systemId The ID of the system to delete
     */
    @Transactional
    public void deleteSystem(String systemId) {
        log.info("Deleting enterprise system: {}", systemId);
        
        enterpriseSystemRepository.deleteById(systemId);
    }

    /**
     * Execute an integration operation.
     *
     * @param request The integration request
     * @return The integration response
     */
    public IntegrationResponseDto executeOperation(IntegrationRequestDto request) {
        String requestId = UUID.randomUUID().toString();
        long startTime = System.currentTimeMillis();
        
        log.info("Executing integration operation. RequestId: {}, SystemId: {}, Operation: {}", 
                requestId, request.getSystemId(), request.getOperation());
        
        try {
            // Get system configuration
            EnterpriseSystem system = enterpriseSystemRepository.findById(request.getSystemId())
                    .orElseThrow(() -> new RuntimeException("System not found: " + request.getSystemId()));
            
            if (!system.isEnabled()) {
                throw new RuntimeException("System is disabled: " + request.getSystemId());
            }
            
            // Get credentials
            Map<String, String> credentials = securityService.getCredentials(request.getSystemId());
            
            // Execute operation
            Map<String, Object> result = adapterService.executeOperation(
                    system.getSystemType(),
                    request.getOperation(),
                    request.getParams(),
                    credentials
            );
            
            // Log success
            monitoringService.logOperation(
                    request.getSystemId(),
                    request.getOperation(),
                    "success",
                    System.currentTimeMillis() - startTime,
                    requestId,
                    null,
                    request.getContext()
            );
            
            return IntegrationResponseDto.builder()
                    .requestId(requestId)
                    .success(true)
                    .data(result)
                    .executionTimeMs(System.currentTimeMillis() - startTime)
                    .build();
            
        } catch (Exception e) {
            log.error("Error executing integration operation", e);
            
            // Log error
            monitoringService.logOperation(
                    request.getSystemId(),
                    request.getOperation(),
                    "error",
                    System.currentTimeMillis() - startTime,
                    requestId,
                    e.getMessage(),
                    request.getContext()
            );
            
            return IntegrationResponseDto.builder()
                    .requestId(requestId)
                    .success(false)
                    .errorMessage(e.getMessage())
                    .errorCode("INTEGRATION_ERROR")
                    .executionTimeMs(System.currentTimeMillis() - startTime)
                    .build();
        }
    }

    /**
     * Store credentials for an enterprise system.
     *
     * @param systemId The ID of the system
     * @param credentials The credentials to store
     * @return Whether the operation was successful
     */
    public boolean storeCredentials(String systemId, Map<String, String> credentials) {
        log.info("Storing credentials for system: {}", systemId);
        
        return securityService.storeCredentials(systemId, credentials);
    }

    /**
     * Convert entity to DTO.
     *
     * @param entity The entity to convert
     * @return The DTO
     */
    private EnterpriseSystemDto convertToDto(EnterpriseSystem entity) {
        return EnterpriseSystemDto.builder()
                .systemId(entity.getSystemId())
                .systemType(entity.getSystemType())
                .name(entity.getName())
                .description(entity.getDescription())
                .enabled(entity.isEnabled())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .connectionParams(entity.getConnectionParams())
                .authParams(entity.getAuthParams())
                .transformParams(entity.getTransformParams())
                .metadata(entity.getMetadata())
                .build();
    }

    /**
     * Convert DTO to entity.
     *
     * @param dto The DTO to convert
     * @return The entity
     */
    private EnterpriseSystem convertToEntity(EnterpriseSystemDto dto) {
        return EnterpriseSystem.builder()
                .systemId(dto.getSystemId())
                .systemType(dto.getSystemType())
                .name(dto.getName())
                .description(dto.getDescription())
                .enabled(dto.isEnabled())
                .connectionParams(dto.getConnectionParams())
                .authParams(dto.getAuthParams())
                .transformParams(dto.getTransformParams())
                .metadata(dto.getMetadata())
                .build();
    }
}
