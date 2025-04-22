package ai.lumina.provider.controller;

import ai.lumina.provider.dto.ProviderCapabilityDto;
import ai.lumina.provider.service.ProviderCapabilityService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/providers/capabilities")
@RequiredArgsConstructor
public class ProviderCapabilityController {

    private final ProviderCapabilityService capabilityService;

    @GetMapping
    public ResponseEntity<List<ProviderCapabilityDto>> getAllCapabilities() {
        List<ProviderCapabilityDto> capabilities = capabilityService.getAllCapabilities();
        return ResponseEntity.ok(capabilities);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProviderCapabilityDto> getCapabilityById(@PathVariable Long id) {
        return capabilityService.getCapabilityById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/provider/{providerId}")
    public ResponseEntity<List<ProviderCapabilityDto>> getCapabilitiesByProviderId(@PathVariable Long providerId) {
        List<ProviderCapabilityDto> capabilities = capabilityService.getCapabilitiesByProviderId(providerId);
        return ResponseEntity.ok(capabilities);
    }

    @GetMapping("/category/{category}")
    public ResponseEntity<List<ProviderCapabilityDto>> getCapabilitiesByCategory(@PathVariable String category) {
        List<ProviderCapabilityDto> capabilities = capabilityService.getCapabilitiesByCategory(category);
        return ResponseEntity.ok(capabilities);
    }

    @GetMapping("/verified")
    public ResponseEntity<List<ProviderCapabilityDto>> getVerifiedCapabilities() {
        List<ProviderCapabilityDto> capabilities = capabilityService.getVerifiedCapabilities();
        return ResponseEntity.ok(capabilities);
    }

    @GetMapping("/name/{capabilityName}")
    public ResponseEntity<List<ProviderCapabilityDto>> getCapabilitiesByName(@PathVariable String capabilityName) {
        List<ProviderCapabilityDto> capabilities = capabilityService.getCapabilitiesByName(capabilityName);
        return ResponseEntity.ok(capabilities);
    }

    @GetMapping("/benchmark")
    public ResponseEntity<List<ProviderCapabilityDto>> getCapabilitiesOrderedByBenchmarkScore() {
        List<ProviderCapabilityDto> capabilities = capabilityService.getCapabilitiesOrderedByBenchmarkScore();
        return ResponseEntity.ok(capabilities);
    }

    @PostMapping
    public ResponseEntity<ProviderCapabilityDto> createCapability(@RequestBody ProviderCapabilityDto capabilityDto) {
        return capabilityService.createCapability(capabilityDto)
                .map(created -> ResponseEntity.status(HttpStatus.CREATED).body(created))
                .orElse(ResponseEntity.badRequest().build());
    }

    @PutMapping("/{id}")
    public ResponseEntity<ProviderCapabilityDto> updateCapability(
            @PathVariable Long id, 
            @RequestBody ProviderCapabilityDto capabilityDto) {
        return capabilityService.updateCapability(id, capabilityDto)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCapability(@PathVariable Long id) {
        boolean deleted = capabilityService.deleteCapability(id);
        return deleted ? 
                ResponseEntity.noContent().build() : 
                ResponseEntity.notFound().build();
    }
}
