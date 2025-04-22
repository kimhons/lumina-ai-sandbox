package ai.lumina.ui.adaptive;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

/**
 * Main application class for the UI Service with Adaptive UI support.
 * This service provides REST endpoints and WebSocket support for the Adaptive UI system.
 */
@SpringBootApplication
@ComponentScan(basePackages = {"ai.lumina.ui.adaptive"})
public class UIServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(UIServiceApplication.class, args);
    }
}
