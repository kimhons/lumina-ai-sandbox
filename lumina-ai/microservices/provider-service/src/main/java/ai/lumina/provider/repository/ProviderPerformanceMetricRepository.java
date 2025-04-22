package ai.lumina.provider.repository;

import ai.lumina.provider.model.ProviderPerformanceMetric;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ProviderPerformanceMetricRepository extends JpaRepository<ProviderPerformanceMetric, Long> {
    
    List<ProviderPerformanceMetric> findByProviderId(Long providerId);
    
    List<ProviderPerformanceMetric> findByModelId(Long modelId);
    
    List<ProviderPerformanceMetric> findByMetricName(String metricName);
    
    @Query("SELECT m FROM ProviderPerformanceMetric m WHERE m.provider.id = :providerId AND m.timestamp >= :startTime AND m.timestamp <= :endTime")
    List<ProviderPerformanceMetric> findByProviderIdAndTimeRange(Long providerId, LocalDateTime startTime, LocalDateTime endTime);
    
    @Query("SELECT m FROM ProviderPerformanceMetric m WHERE m.model.id = :modelId AND m.timestamp >= :startTime AND m.timestamp <= :endTime")
    List<ProviderPerformanceMetric> findByModelIdAndTimeRange(Long modelId, LocalDateTime startTime, LocalDateTime endTime);
    
    @Query("SELECT AVG(m.metricValue) FROM ProviderPerformanceMetric m WHERE m.provider.id = :providerId AND m.metricName = :metricName")
    Double getAverageMetricForProvider(Long providerId, String metricName);
    
    @Query("SELECT AVG(m.metricValue) FROM ProviderPerformanceMetric m WHERE m.model.id = :modelId AND m.metricName = :metricName")
    Double getAverageMetricForModel(Long modelId, String metricName);
}
