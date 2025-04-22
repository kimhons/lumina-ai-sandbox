package ai.lumina.security;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

/**
 * Main application class for the Security Service.
 * This service provides enterprise-grade security capabilities for Lumina AI.
 * 
 * @author Lumina AI Team
 */
@SpringBootApplication
@EnableDiscoveryClient
public class SecurityServiceApplication {

    /**
     * Main method to start the Security Service application.
     * 
     * @param args Command line arguments
     */
    public static void main(String[] args) {
        SpringApplication.run(SecurityServiceApplication.class, args);
    }
}
