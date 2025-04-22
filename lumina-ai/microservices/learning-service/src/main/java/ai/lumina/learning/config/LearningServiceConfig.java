package ai.lumina.learning.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

/**
 * Configuration class for the Learning Service.
 * Provides beans for external communication and integration.
 */
@Configuration
public class LearningServiceConfig {

    /**
     * Creates a RestTemplate bean for making HTTP requests to other services.
     * 
     * @return RestTemplate instance
     */
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
