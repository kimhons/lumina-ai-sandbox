package ai.lumina.provider.service;

import ai.lumina.provider.dto.ProviderDto;
import ai.lumina.provider.dto.ProviderModelDto;
import ai.lumina.provider.dto.ProviderCapabilityDto;
import ai.lumina.provider.model.Provider;
import ai.lumina.provider.model.ProviderModel;
import ai.lumina.provider.model.ProviderCapability;
import ai.lumina.provider.repository.ProviderRepository;
import ai.lumina.provider.repository.ProviderModelRepository;
import ai.lumina.provider.repository.ProviderCapabilityRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ProviderService {

    private final ProviderRepository providerRepository;
    private final ProviderModelRepository modelRepository;
    private final ProviderCapabilityRepository capabilityRepository;

    @Transactional(readOnly = true)
    public List<ProviderDto> getAllProviders() {
        return providerRepository.findAll().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderDto> getEnabledProviders() {
        return providerRepository.findByEnabledTrue().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Optional<ProviderDto> getProviderById(Long id) {
        return providerRepository.findById(id)
                .map(this::mapToDto);
    }

    @Transactional(readOnly = true)
    public Optional<ProviderDto> getProviderByName(String name) {
        return providerRepository.findByName(name)
                .map(this::mapToDto);
    }

    @Transactional
    public ProviderDto createProvider(ProviderDto providerDto) {
        Provider provider = mapToEntity(providerDto);
        Provider savedProvider = providerRepository.save(provider);
        return mapToDto(savedProvider);
    }

    @Transactional
    public Optional<ProviderDto> updateProvider(Long id, ProviderDto providerDto) {
        return providerRepository.findById(id)
                .map(provider -> {
                    updateProviderFromDto(provider, providerDto);
                    Provider updatedProvider = providerRepository.save(provider);
                    return mapToDto(updatedProvider);
                });
    }

    @Transactional
    public boolean deleteProvider(Long id) {
        if (providerRepository.existsById(id)) {
            providerRepository.deleteById(id);
            return true;
        }
        return false;
    }

    @Transactional(readOnly = true)
    public List<ProviderDto> getProvidersByCapability(String capability) {
        return providerRepository.findByCapability(capability).stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderDto> getProvidersSupportingStreaming() {
        return providerRepository.findAllSupportingStreaming().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderDto> getProvidersSupportingFunctions() {
        return providerRepository.findAllSupportingFunctions().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderDto> getProvidersSupportingVision() {
        return providerRepository.findAllSupportingVision().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    // Helper methods for mapping between entities and DTOs
    private ProviderDto mapToDto(Provider provider) {
        Set<ProviderModelDto> modelDtos = provider.getModels().stream()
                .map(this::mapToDto)
                .collect(Collectors.toSet());
                
        Set<ProviderCapabilityDto> capabilityDtos = provider.getCapabilities().stream()
                .map(this::mapToDto)
                .collect(Collectors.toSet());
                
        return ProviderDto.builder()
                .id(provider.getId())
                .name(provider.getName())
                .apiEndpoint(provider.getApiEndpoint())
                .apiVersion(provider.getApiVersion())
                .enabled(provider.isEnabled())
                .description(provider.getDescription())
                .authType(provider.getAuthType() != null ? provider.getAuthType().name() : null)
                .costPer1kTokensInput(provider.getCostPer1kTokensInput())
                .costPer1kTokensOutput(provider.getCostPer1kTokensOutput())
                .maxTokens(provider.getMaxTokens())
                .supportsStreaming(provider.isSupportsStreaming())
                .supportsFunctions(provider.isSupportsFunctions())
                .supportsVision(provider.isSupportsVision())
                .supportsEmbeddings(provider.isSupportsEmbeddings())
                .models(modelDtos)
                .capabilities(capabilityDtos)
                .createdAt(provider.getCreatedAt())
                .updatedAt(provider.getUpdatedAt())
                .build();
    }

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

    private ProviderCapabilityDto mapToDto(ProviderCapability capability) {
        return ProviderCapabilityDto.builder()
                .id(capability.getId())
                .providerId(capability.getProvider().getId())
                .name(capability.getName())
                .category(capability.getCategory())
                .description(capability.getDescription())
                .capabilityLevel(capability.getCapabilityLevel())
                .benchmarkScore(capability.getBenchmarkScore())
                .isVerified(capability.isVerified())
                .createdAt(capability.getCreatedAt())
                .updatedAt(capability.getUpdatedAt())
                .build();
    }

    private Provider mapToEntity(ProviderDto dto) {
        Provider provider = Provider.builder()
                .name(dto.getName())
                .apiEndpoint(dto.getApiEndpoint())
                .apiVersion(dto.getApiVersion())
                .enabled(dto.isEnabled())
                .description(dto.getDescription())
                .authType(dto.getAuthType() != null ? Provider.AuthType.valueOf(dto.getAuthType()) : null)
                .costPer1kTokensInput(dto.getCostPer1kTokensInput())
                .costPer1kTokensOutput(dto.getCostPer1kTokensOutput())
                .maxTokens(dto.getMaxTokens())
                .supportsStreaming(dto.isSupportsStreaming())
                .supportsFunctions(dto.isSupportsFunctions())
                .supportsVision(dto.isSupportsVision())
                .supportsEmbeddings(dto.isSupportsEmbeddings())
                .build();
                
        if (dto.getId() != null) {
            provider.setId(dto.getId());
        }
        
        return provider;
    }

    private void updateProviderFromDto(Provider provider, ProviderDto dto) {
        provider.setName(dto.getName());
        provider.setApiEndpoint(dto.getApiEndpoint());
        provider.setApiVersion(dto.getApiVersion());
        provider.setEnabled(dto.isEnabled());
        provider.setDescription(dto.getDescription());
        provider.setAuthType(dto.getAuthType() != null ? Provider.AuthType.valueOf(dto.getAuthType()) : null);
        provider.setCostPer1kTokensInput(dto.getCostPer1kTokensInput());
        provider.setCostPer1kTokensOutput(dto.getCostPer1kTokensOutput());
        provider.setMaxTokens(dto.getMaxTokens());
        provider.setSupportsStreaming(dto.isSupportsStreaming());
        provider.setSupportsFunctions(dto.isSupportsFunctions());
        provider.setSupportsVision(dto.isSupportsVision());
        provider.setSupportsEmbeddings(dto.isSupportsEmbeddings());
    }
}
