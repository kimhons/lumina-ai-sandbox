package ai.lumina.provider.service;

import ai.lumina.provider.dto.ProviderCapabilityDto;
import ai.lumina.provider.model.Provider;
import ai.lumina.provider.model.ProviderCapability;
import ai.lumina.provider.repository.ProviderCapabilityRepository;
import ai.lumina.provider.repository.ProviderRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ProviderCapabilityService {

    private final ProviderCapabilityRepository capabilityRepository;
    private final ProviderRepository providerRepository;

    @Transactional(readOnly = true)
    public List<ProviderCapabilityDto> getAllCapabilities() {
        return capabilityRepository.findAll().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Optional<ProviderCapabilityDto> getCapabilityById(Long id) {
        return capabilityRepository.findById(id)
                .map(this::mapToDto);
    }

    @Transactional(readOnly = true)
    public List<ProviderCapabilityDto> getCapabilitiesByProviderId(Long providerId) {
        return capabilityRepository.findByProviderId(providerId).stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderCapabilityDto> getCapabilitiesByCategory(String category) {
        return capabilityRepository.findByCategory(category).stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderCapabilityDto> getVerifiedCapabilities() {
        return capabilityRepository.findAllVerifiedFromEnabledProviders().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderCapabilityDto> getCapabilitiesByName(String capabilityName) {
        return capabilityRepository.findAllByCapabilityName(capabilityName).stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderCapabilityDto> getCapabilitiesOrderedByBenchmarkScore() {
        return capabilityRepository.findAllOrderByBenchmarkScore().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional
    public Optional<ProviderCapabilityDto> createCapability(ProviderCapabilityDto capabilityDto) {
        return providerRepository.findById(capabilityDto.getProviderId())
                .map(provider -> {
                    ProviderCapability capability = mapToEntity(capabilityDto, provider);
                    ProviderCapability savedCapability = capabilityRepository.save(capability);
                    return mapToDto(savedCapability);
                });
    }

    @Transactional
    public Optional<ProviderCapabilityDto> updateCapability(Long id, ProviderCapabilityDto capabilityDto) {
        return capabilityRepository.findById(id)
                .flatMap(capability -> providerRepository.findById(capabilityDto.getProviderId())
                        .map(provider -> {
                            updateCapabilityFromDto(capability, capabilityDto, provider);
                            ProviderCapability updatedCapability = capabilityRepository.save(capability);
                            return mapToDto(updatedCapability);
                        }));
    }

    @Transactional
    public boolean deleteCapability(Long id) {
        if (capabilityRepository.existsById(id)) {
            capabilityRepository.deleteById(id);
            return true;
        }
        return false;
    }

    // Helper methods for mapping between entities and DTOs
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

    private ProviderCapability mapToEntity(ProviderCapabilityDto dto, Provider provider) {
        ProviderCapability capability = ProviderCapability.builder()
                .provider(provider)
                .name(dto.getName())
                .category(dto.getCategory())
                .description(dto.getDescription())
                .capabilityLevel(dto.getCapabilityLevel())
                .benchmarkScore(dto.getBenchmarkScore())
                .isVerified(dto.isVerified())
                .build();
                
        if (dto.getId() != null) {
            capability.setId(dto.getId());
        }
        
        return capability;
    }

    private void updateCapabilityFromDto(ProviderCapability capability, ProviderCapabilityDto dto, Provider provider) {
        capability.setProvider(provider);
        capability.setName(dto.getName());
        capability.setCategory(dto.getCategory());
        capability.setDescription(dto.getDescription());
        capability.setCapabilityLevel(dto.getCapabilityLevel());
        capability.setBenchmarkScore(dto.getBenchmarkScore());
        capability.setVerified(dto.isVerified());
    }
}
