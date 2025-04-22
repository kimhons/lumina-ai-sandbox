package ai.lumina.memory;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.openfeign.EnableFeignClients;

/**
 * Main application class for the Memory Service.
 * This service provides advanced memory capabilities for Lumina AI including:
 * - Neural context compression
 * - Hierarchical memory management
 * - Cross-session memory persistence
 * - Optimized memory retrieval
 */
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients
public class MemoryServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(MemoryServiceApplication.class, args);
    }
}
