package ai.lumina.provider.service;

import ai.lumina.provider.dto.ProviderPerformanceMetricDto;
import ai.lumina.provider.model.Provider;
import ai.lumina.provider.model.ProviderModel;
import ai.lumina.provider.model.ProviderPerformanceMetric;
import ai.lumina.provider.repository.ProviderModelRepository;
import ai.lumina.provider.repository.ProviderPerformanceMetricRepository;
import ai.lumina.provider.repository.ProviderRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ProviderPerformanceMetricService {

    private final ProviderPerformanceMetricRepository metricRepository;
    private final ProviderRepository providerRepository;
    private final ProviderModelRepository modelRepository;

    @Transactional(readOnly = true)
    public List<ProviderPerformanceMetricDto> getAllMetrics() {
        return metricRepository.findAll().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Optional<ProviderPerformanceMetricDto> getMetricById(Long id) {
        return metricRepository.findById(id)
                .map(this::mapToDto);
    }

    @Transactional(readOnly = true)
    public List<ProviderPerformanceMetricDto> getMetricsByProviderId(Long providerId) {
        return metricRepository.findByProviderId(providerId).stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderPerformanceMetricDto> getMetricsByModelId(Long modelId) {
        return metricRepository.findByModelId(modelId).stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderPerformanceMetricDto> getMetricsByName(String metricName) {
        return metricRepository.findByMetricName(metricName).stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderPerformanceMetricDto> getMetricsByProviderIdAndTimeRange(
            Long providerId, LocalDateTime startTime, LocalDateTime endTime) {
        return metricRepository.findByProviderIdAndTimeRange(providerId, startTime, endTime).stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<ProviderPerformanceMetricDto> getMetricsByModelIdAndTimeRange(
            Long modelId, LocalDateTime startTime, LocalDateTime endTime) {
        return metricRepository.findByModelIdAndTimeRange(modelId, startTime, endTime).stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Double getAverageMetricForProvider(Long providerId, String metricName) {
        return metricRepository.getAverageMetricForProvider(providerId, metricName);
    }

    @Transactional(readOnly = true)
    public Double getAverageMetricForModel(Long modelId, String metricName) {
        return metricRepository.getAverageMetricForModel(modelId, metricName);
    }

    @Transactional
    public Optional<ProviderPerformanceMetricDto> createMetric(ProviderPerformanceMetricDto metricDto) {
        return providerRepository.findById(metricDto.getProviderId())
                .flatMap(provider -> {
                    Optional<ProviderModel> modelOpt = metricDto.getModelId() != null ?
                            modelRepository.findById(metricDto.getModelId()) : Optional.empty();
                    
                    ProviderPerformanceMetric metric = mapToEntity(metricDto, provider, modelOpt.orElse(null));
                    ProviderPerformanceMetric savedMetric = metricRepository.save(metric);
                    return Optional.of(mapToDto(savedMetric));
                });
    }

    @Transactional
    public Optional<ProviderPerformanceMetricDto> updateMetric(Long id, ProviderPerformanceMetricDto metricDto) {
        return metricRepository.findById(id)
                .flatMap(metric -> providerRepository.findById(metricDto.getProviderId())
                        .flatMap(provider -> {
                            Optional<ProviderModel> modelOpt = metricDto.getModelId() != null ?
                                    modelRepository.findById(metricDto.getModelId()) : Optional.empty();
                            
                            updateMetricFromDto(metric, metricDto, provider, modelOpt.orElse(null));
                            ProviderPerformanceMetric updatedMetric = metricRepository.save(metric);
                            return Optional.of(mapToDto(updatedMetric));
                        }));
    }

    @Transactional
    public boolean deleteMetric(Long id) {
        if (metricRepository.existsById(id)) {
            metricRepository.deleteById(id);
            return true;
        }
        return false;
    }

    // Helper methods for mapping between entities and DTOs
    private ProviderPerformanceMetricDto mapToDto(ProviderPerformanceMetric metric) {
        return ProviderPerformanceMetricDto.builder()
                .id(metric.getId())
                .providerId(metric.getProvider().getId())
                .modelId(metric.getModel() != null ? metric.getModel().getId() : null)
                .metricName(metric.getMetricName())
                .metricValue(metric.getMetricValue())
                .timestamp(metric.getTimestamp())
                .context(metric.getContext())
                .createdAt(metric.getCreatedAt())
                .updatedAt(metric.getUpdatedAt())
                .build();
    }

    private ProviderPerformanceMetric mapToEntity(ProviderPerformanceMetricDto dto, Provider provider, ProviderModel model) {
        ProviderPerformanceMetric metric = ProviderPerformanceMetric.builder()
                .provider(provider)
                .model(model)
                .metricName(dto.getMetricName())
                .metricValue(dto.getMetricValue())
                .timestamp(dto.getTimestamp() != null ? dto.getTimestamp() : LocalDateTime.now())
                .context(dto.getContext())
                .build();
                
        if (dto.getId() != null) {
            metric.setId(dto.getId());
        }
        
        return metric;
    }

    private void updateMetricFromDto(ProviderPerformanceMetric metric, ProviderPerformanceMetricDto dto, 
                                    Provider provider, ProviderModel model) {
        metric.setProvider(provider);
        metric.setModel(model);
        metric.setMetricName(dto.getMetricName());
        metric.setMetricValue(dto.getMetricValue());
        metric.setTimestamp(dto.getTimestamp() != null ? dto.getTimestamp() : LocalDateTime.now());
        metric.setContext(dto.getContext());
    }
}
