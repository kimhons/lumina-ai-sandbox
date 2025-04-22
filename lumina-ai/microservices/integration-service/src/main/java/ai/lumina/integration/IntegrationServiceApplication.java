"""
Integration Service for Lumina AI Microservices Architecture.

This module implements the Integration Service for connecting with enterprise systems,
providing a RESTful API for other microservices to interact with external enterprise systems.
"""

package ai.lumina.integration;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.context.annotation.ComponentScan;

@SpringBootApplication
@EnableDiscoveryClient
@ComponentScan(basePackages = {"ai.lumina.integration"})
public class IntegrationServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(IntegrationServiceApplication.class, args);
    }
}
