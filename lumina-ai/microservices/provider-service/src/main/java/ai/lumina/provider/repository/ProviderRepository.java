package ai.lumina.provider.repository;

import ai.lumina.provider.model.Provider;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProviderRepository extends JpaRepository<Provider, Long> {
    
    Optional<Provider> findByName(String name);
    
    List<Provider> findByEnabledTrue();
    
    @Query("SELECT p FROM Provider p WHERE p.enabled = true AND :capability MEMBER OF p.capabilities.name")
    List<Provider> findByCapability(String capability);
    
    @Query("SELECT p FROM Provider p JOIN p.models m WHERE m.supportsStreaming = true AND p.enabled = true")
    List<Provider> findAllSupportingStreaming();
    
    @Query("SELECT p FROM Provider p JOIN p.models m WHERE m.supportsFunctions = true AND p.enabled = true")
    List<Provider> findAllSupportingFunctions();
    
    @Query("SELECT p FROM Provider p JOIN p.models m WHERE m.supportsVision = true AND p.enabled = true")
    List<Provider> findAllSupportingVision();
}
