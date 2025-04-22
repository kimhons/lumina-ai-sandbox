package ai.lumina.provider.controller;

import ai.lumina.provider.dto.ProviderModelDto;
import ai.lumina.provider.service.ProviderModelService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/providers/models")
@RequiredArgsConstructor
public class ProviderModelController {

    private final ProviderModelService modelService;

    @GetMapping
    public ResponseEntity<List<ProviderModelDto>> getAllModels(
            @RequestParam(required = false, defaultValue = "false") boolean enabledOnly) {
        List<ProviderModelDto> models = enabledOnly ? 
                modelService.getEnabledModels() : 
                modelService.getAllModels();
        return ResponseEntity.ok(models);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProviderModelDto> getModelById(@PathVariable Long id) {
        return modelService.getModelById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/provider/{providerId}")
    public ResponseEntity<List<ProviderModelDto>> getModelsByProviderId(@PathVariable Long providerId) {
        List<ProviderModelDto> models = modelService.getModelsByProviderId(providerId);
        return ResponseEntity.ok(models);
    }

    @GetMapping("/provider/{providerId}/model/{modelId}")
    public ResponseEntity<ProviderModelDto> getModelByProviderIdAndModelId(
            @PathVariable Long providerId, 
            @PathVariable String modelId) {
        return modelService.getModelByProviderIdAndModelId(providerId, modelId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<ProviderModelDto> createModel(@RequestBody ProviderModelDto modelDto) {
        return modelService.createModel(modelDto)
                .map(created -> ResponseEntity.status(HttpStatus.CREATED).body(created))
                .orElse(ResponseEntity.badRequest().build());
    }

    @PutMapping("/{id}")
    public ResponseEntity<ProviderModelDto> updateModel(
            @PathVariable Long id, 
            @RequestBody ProviderModelDto modelDto) {
        return modelService.updateModel(id, modelDto)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteModel(@PathVariable Long id) {
        boolean deleted = modelService.deleteModel(id);
        return deleted ? 
                ResponseEntity.noContent().build() : 
                ResponseEntity.notFound().build();
    }

    @GetMapping("/streaming")
    public ResponseEntity<List<ProviderModelDto>> getModelsSupportingStreaming() {
        List<ProviderModelDto> models = modelService.getModelsSupportingStreaming();
        return ResponseEntity.ok(models);
    }

    @GetMapping("/functions")
    public ResponseEntity<List<ProviderModelDto>> getModelsSupportingFunctions() {
        List<ProviderModelDto> models = modelService.getModelsSupportingFunctions();
        return ResponseEntity.ok(models);
    }

    @GetMapping("/vision")
    public ResponseEntity<List<ProviderModelDto>> getModelsSupportingVision() {
        List<ProviderModelDto> models = modelService.getModelsSupportingVision();
        return ResponseEntity.ok(models);
    }

    @GetMapping("/performance")
    public ResponseEntity<List<ProviderModelDto>> getModelsOrderedByPerformance() {
        List<ProviderModelDto> models = modelService.getModelsOrderedByPerformance();
        return ResponseEntity.ok(models);
    }

    @GetMapping("/cost")
    public ResponseEntity<List<ProviderModelDto>> getModelsOrderedByCost() {
        List<ProviderModelDto> models = modelService.getModelsOrderedByCost();
        return ResponseEntity.ok(models);
    }
}
