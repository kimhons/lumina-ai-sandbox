package ai.lumina.monitoring;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

/**
 * Main application class for the Monitoring Service.
 * This service provides comprehensive monitoring, performance optimization,
 * analytics, and enterprise deployment capabilities for Lumina AI.
 */
@SpringBootApplication
@EnableScheduling
@EnableDiscoveryClient
public class MonitoringServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(MonitoringServiceApplication.class, args);
    }
}
