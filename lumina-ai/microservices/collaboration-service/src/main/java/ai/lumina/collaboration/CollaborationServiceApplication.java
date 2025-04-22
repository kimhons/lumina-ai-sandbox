package ai.lumina.collaboration;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * Main application class for the Collaboration Service.
 * This service provides advanced multi-agent collaboration capabilities
 * including dynamic team formation, negotiation protocols, shared context
 * management, collaborative learning, and workflow orchestration.
 */
@SpringBootApplication
@EnableDiscoveryClient
@EnableAsync
public class CollaborationServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(CollaborationServiceApplication.class, args);
    }
}
