package ai.lumina.provider.repository;

import ai.lumina.provider.model.ProviderModel;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProviderModelRepository extends JpaRepository<ProviderModel, Long> {
    
    List<ProviderModel> findByProviderId(Long providerId);
    
    Optional<ProviderModel> findByProviderIdAndModelId(Long providerId, String modelId);
    
    List<ProviderModel> findByEnabledTrue();
    
    @Query("SELECT m FROM ProviderModel m WHERE m.enabled = true AND m.supportsStreaming = true")
    List<ProviderModel> findAllSupportingStreaming();
    
    @Query("SELECT m FROM ProviderModel m WHERE m.enabled = true AND m.supportsFunctions = true")
    List<ProviderModel> findAllSupportingFunctions();
    
    @Query("SELECT m FROM ProviderModel m WHERE m.enabled = true AND m.supportsVision = true")
    List<ProviderModel> findAllSupportingVision();
    
    @Query("SELECT m FROM ProviderModel m WHERE m.enabled = true ORDER BY m.performanceRating DESC")
    List<ProviderModel> findAllOrderByPerformanceRating();
    
    @Query("SELECT m FROM ProviderModel m WHERE m.enabled = true ORDER BY m.costPer1kTokensOutput ASC")
    List<ProviderModel> findAllOrderByCostAsc();
}
