package ai.lumina.provider.repository;

import ai.lumina.provider.model.ProviderCapability;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ProviderCapabilityRepository extends JpaRepository<ProviderCapability, Long> {
    
    List<ProviderCapability> findByProviderId(Long providerId);
    
    List<ProviderCapability> findByCategory(String category);
    
    @Query("SELECT c FROM ProviderCapability c WHERE c.provider.enabled = true AND c.isVerified = true")
    List<ProviderCapability> findAllVerifiedFromEnabledProviders();
    
    @Query("SELECT c FROM ProviderCapability c WHERE c.provider.enabled = true AND c.name = :capabilityName")
    List<ProviderCapability> findAllByCapabilityName(String capabilityName);
    
    @Query("SELECT c FROM ProviderCapability c WHERE c.provider.enabled = true ORDER BY c.benchmarkScore DESC")
    List<ProviderCapability> findAllOrderByBenchmarkScore();
}
