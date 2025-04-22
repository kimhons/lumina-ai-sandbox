package ai.lumina.provider.service;

import ai.lumina.provider.dto.ProviderModelDto;
import ai.lumina.provider.model.Provider;
import ai.lumina.provider.model.ProviderModel;
import ai.lumina.provider.repository.ProviderModelRepository;
import ai.lumina.provider.repository.ProviderRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ProviderModelService {

    private final ProviderModelRepository modelRepository;
    private final ProviderRepository providerRepository;

    @Transactional(readOnly = true)
    public List<ProviderModelDto> getAllModels() {
        return modelRepository.findAll().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderModelDto> getEnabledModels() {
        return modelRepository.findByEnabledTrue().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Optional<ProviderModelDto> getModelById(Long id) {
        return modelRepository.findById(id)
                .map(this::mapToDto);
    }

    @Transactional(readOnly = true)
    public List<ProviderModelDto> getModelsByProviderId(Long providerId) {
        return modelRepository.findByProviderId(providerId).stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Optional<ProviderModelDto> getModelByProviderIdAndModelId(Long providerId, String modelId) {
        return modelRepository.findByProviderIdAndModelId(providerId, modelId)
                .map(this::mapToDto);
    }

    @Transactional
    public Optional<ProviderModelDto> createModel(ProviderModelDto modelDto) {
        return providerRepository.findById(modelDto.getProviderId())
                .map(provider -> {
                    ProviderModel model = mapToEntity(modelDto, provider);
                    ProviderModel savedModel = modelRepository.save(model);
                    return mapToDto(savedModel);
                });
    }

    @Transactional
    public Optional<ProviderModelDto> updateModel(Long id, ProviderModelDto modelDto) {
        return modelRepository.findById(id)
                .flatMap(model -> providerRepository.findById(modelDto.getProviderId())
                        .map(provider -> {
                            updateModelFromDto(model, modelDto, provider);
                            ProviderModel updatedModel = modelRepository.save(model);
                            return mapToDto(updatedModel);
                        }));
    }

    @Transactional
    public boolean deleteModel(Long id) {
        if (modelRepository.existsById(id)) {
            modelRepository.deleteById(id);
            return true;
        }
        return false;
    }

    @Transactional(readOnly = true)
    public List<ProviderModelDto> getModelsSupportingStreaming() {
        return modelRepository.findAllSupportingStreaming().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderModelDto> getModelsSupportingFunctions() {
        return modelRepository.findAllSupportingFunctions().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderModelDto> getModelsSupportingVision() {
        return modelRepository.findAllSupportingVision().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderModelDto> getModelsOrderedByPerformance() {
        return modelRepository.findAllOrderByPerformanceRating().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderModelDto> getModelsOrderedByCost() {
        return modelRepository.findAllOrderByCostAsc().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    // Helper methods for mapping between entities and DTOs
    private ProviderModelDto mapToDto(ProviderModel model) {
        return ProviderModelDto.builder()
                .id(model.getId())
                .providerId(model.getProvider().getId())
                .name(model.getName())
                .modelId(model.getModelId())
                .description(model.getDescription())
                .maxTokens(model.getMaxTokens())
                .contextWindow(model.getContextWindow())
                .costPer1kTokensInput(model.getCostPer1kTokensInput())
                .costPer1kTokensOutput(model.getCostPer1kTokensOutput())
                .supportsStreaming(model.isSupportsStreaming())
                .supportsFunctions(model.isSupportsFunctions())
                .supportsVision(model.isSupportsVision())
                .supportsEmbeddings(model.isSupportsEmbeddings())
                .enabled(model.isEnabled())
                .performanceRating(model.getPerformanceRating())
                .createdAt(model.getCreatedAt())
                .updatedAt(model.getUpdatedAt())
                .build();
    }

    private ProviderModel mapToEntity(ProviderModelDto dto, Provider provider) {
        ProviderModel model = ProviderModel.builder()
                .provider(provider)
                .name(dto.getName())
                .modelId(dto.getModelId())
                .description(dto.getDescription())
                .maxTokens(dto.getMaxTokens())
                .contextWindow(dto.getContextWindow())
                .costPer1kTokensInput(dto.getCostPer1kTokensInput())
                .costPer1kTokensOutput(dto.getCostPer1kTokensOutput())
                .supportsStreaming(dto.isSupportsStreaming())
                .supportsFunctions(dto.isSupportsFunctions())
                .supportsVision(dto.isSupportsVision())
                .supportsEmbeddings(dto.isSupportsEmbeddings())
                .enabled(dto.isEnabled())
                .performanceRating(dto.getPerformanceRating())
                .build();
                
        if (dto.getId() != null) {
            model.setId(dto.getId());
        }
        
        return model;
    }

    private void updateModelFromDto(ProviderModel model, ProviderModelDto dto, Provider provider) {
        model.setProvider(provider);
        model.setName(dto.getName());
        model.setModelId(dto.getModelId());
        model.setDescription(dto.getDescription());
        model.setMaxTokens(dto.getMaxTokens());
        model.setContextWindow(dto.getContextWindow());
        model.setCostPer1kTokensInput(dto.getCostPer1kTokensInput());
        model.setCostPer1kTokensOutput(dto.getCostPer1kTokensOutput());
        model.setSupportsStreaming(dto.isSupportsStreaming());
        model.setSupportsFunctions(dto.isSupportsFunctions());
        model.setSupportsVision(dto.isSupportsVision());
        model.setSupportsEmbeddings(dto.isSupportsEmbeddings());
        model.setEnabled(dto.isEnabled());
        model.setPerformanceRating(dto.getPerformanceRating());
    }
}
