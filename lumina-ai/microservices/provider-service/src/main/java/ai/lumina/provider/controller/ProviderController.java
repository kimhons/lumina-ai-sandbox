package ai.lumina.provider.controller;

import ai.lumina.provider.dto.ProviderDto;
import ai.lumina.provider.service.ProviderService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/providers")
@RequiredArgsConstructor
public class ProviderController {

    private final ProviderService providerService;

    @GetMapping
    public ResponseEntity<List<ProviderDto>> getAllProviders(
            @RequestParam(required = false, defaultValue = "false") boolean enabledOnly) {
        List<ProviderDto> providers = enabledOnly ? 
                providerService.getEnabledProviders() : 
                providerService.getAllProviders();
        return ResponseEntity.ok(providers);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProviderDto> getProviderById(@PathVariable Long id) {
        return providerService.getProviderById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/name/{name}")
    public ResponseEntity<ProviderDto> getProviderByName(@PathVariable String name) {
        return providerService.getProviderByName(name)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<ProviderDto> createProvider(@RequestBody ProviderDto providerDto) {
        ProviderDto createdProvider = providerService.createProvider(providerDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdProvider);
    }

    @PutMapping("/{id}")
    public ResponseEntity<ProviderDto> updateProvider(
            @PathVariable Long id, 
            @RequestBody ProviderDto providerDto) {
        return providerService.updateProvider(id, providerDto)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProvider(@PathVariable Long id) {
        boolean deleted = providerService.deleteProvider(id);
        return deleted ? 
                ResponseEntity.noContent().build() : 
                ResponseEntity.notFound().build();
    }

    @GetMapping("/capability/{capability}")
    public ResponseEntity<List<ProviderDto>> getProvidersByCapability(
            @PathVariable String capability) {
        List<ProviderDto> providers = providerService.getProvidersByCapability(capability);
        return ResponseEntity.ok(providers);
    }

    @GetMapping("/streaming")
    public ResponseEntity<List<ProviderDto>> getProvidersSupportingStreaming() {
        List<ProviderDto> providers = providerService.getProvidersSupportingStreaming();
        return ResponseEntity.ok(providers);
    }

    @GetMapping("/functions")
    public ResponseEntity<List<ProviderDto>> getProvidersSupportingFunctions() {
        List<ProviderDto> providers = providerService.getProvidersSupportingFunctions();
        return ResponseEntity.ok(providers);
    }

    @GetMapping("/vision")
    public ResponseEntity<List<ProviderDto>> getProvidersSupportingVision() {
        List<ProviderDto> providers = providerService.getProvidersSupportingVision();
        return ResponseEntity.ok(providers);
    }
}
