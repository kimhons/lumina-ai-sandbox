package ai.lumina.apigateway.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/fallback")
public class FallbackController {

    @GetMapping("/provider-service")
    public Mono<String> providerServiceFallback() {
        return Mono.just("Provider Service is currently unavailable. Please try again later.");
    }

    @GetMapping("/memory-service")
    public Mono<String> memoryServiceFallback() {
        return Mono.just("Memory Service is currently unavailable. Please try again later.");
    }

    @GetMapping("/security-service")
    public Mono<String> securityServiceFallback() {
        return Mono.just("Security Service is currently unavailable. Please try again later.");
    }

    @GetMapping("/ui-service")
    public Mono<String> uiServiceFallback() {
        return Mono.just("UI Service is currently unavailable. Please try again later.");
    }

    @GetMapping("/tool-service")
    public Mono<String> toolServiceFallback() {
        return Mono.just("Tool Service is currently unavailable. Please try again later.");
    }

    @GetMapping("/{service}")
    public Mono<String> defaultFallback(@PathVariable String service) {
        return Mono.just(service + " is currently unavailable. Please try again later.");
    }
}
