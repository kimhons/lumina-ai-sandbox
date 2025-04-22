package ai.lumina.collaboration.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.integration.config.EnableIntegration;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.CacheManager;
import org.springframework.cache.concurrent.ConcurrentMapCacheManager;

import java.util.concurrent.Executor;

/**
 * Advanced configuration for the Collaboration Service.
 * This configuration provides enhanced capabilities for the multi-agent collaboration system,
 * including asynchronous processing, caching, and integration with other services.
 */
@Configuration
@EnableAsync
@EnableJpaAuditing
@EnableIntegration
@EnableCaching
public class CollaborationConfig {

    /**
     * Configure the async executor for handling concurrent collaboration tasks.
     * This enables efficient processing of team formation, negotiation, and context management operations.
     */
    @Bean(name = "collaborationTaskExecutor")
    public Executor collaborationTaskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("collab-async-");
        executor.initialize();
        return executor;
    }

    /**
     * Configure cache manager for collaboration service.
     * Caching improves performance for frequently accessed collaboration data.
     */
    @Bean
    public CacheManager collaborationCacheManager() {
        return new ConcurrentMapCacheManager(
            "teams", 
            "agents", 
            "negotiations", 
            "sharedContexts",
            "capabilities",
            "roles",
            "workflows"
        );
    }

    /**
     * Configure memory integration settings.
     * This bean provides configuration for integrating with the Memory Service.
     */
    @Bean
    public MemoryIntegrationConfig memoryIntegrationConfig() {
        return new MemoryIntegrationConfig();
    }

    /**
     * Inner class for Memory Service integration configuration.
     */
    public static class MemoryIntegrationConfig {
        private boolean enableContextCompression = true;
        private boolean enablePersistentMemory = true;
        private int maxContextSize = 10000;
        private int compressionThreshold = 5000;
        
        public boolean isEnableContextCompression() {
            return enableContextCompression;
        }
        
        public boolean isEnablePersistentMemory() {
            return enablePersistentMemory;
        }
        
        public int getMaxContextSize() {
            return maxContextSize;
        }
        
        public int getCompressionThreshold() {
            return compressionThreshold;
        }
    }
}
