package ai.lumina.learning;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

/**
 * Main application class for the Learning Service.
 * This service provides enhanced learning capabilities for Lumina AI,
 * including model registry, feature engineering, algorithm factory,
 * evaluation framework, continuous learning, explainable AI, knowledge transfer,
 * privacy-preserving learning, and integration with the collaboration system.
 */
@SpringBootApplication
@EnableDiscoveryClient
public class LearningServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(LearningServiceApplication.class, args);
    }
    
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
