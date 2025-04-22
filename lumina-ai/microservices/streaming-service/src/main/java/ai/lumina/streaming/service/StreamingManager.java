package ai.lumina.streaming.service;

import ai.lumina.streaming.client.ProviderStreamingClient;
import ai.lumina.streaming.model.StreamingRequest;
import ai.lumina.streaming.model.StreamingResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * Core service for managing streaming requests and responses across different providers.
 */
@Service
@Slf4j
public class StreamingManager {

    private final Map<String, ProviderStreamingClient> clientsByProviderId;

    public StreamingManager(List<ProviderStreamingClient> clients) {
        this.clientsByProviderId = clients.stream()
                .collect(Collectors.toMap(ProviderStreamingClient::getProviderId, Function.identity()));
        log.info("Initialized StreamingManager with {} provider clients: {}", 
                clients.size(), 
                clients.stream().map(ProviderStreamingClient::getProviderId).collect(Collectors.joining(", ")));
    }

    /**
     * Stream a response from the specified provider
     * @param request The unified streaming request
     * @return A Flux of streaming response chunks
     */
    public Flux<StreamingResponse> streamResponse(StreamingRequest request) {
        String providerId = request.getProviderId();
        String modelId = request.getModelId();
        
        log.info("Processing streaming request for provider: {}, model: {}", providerId, modelId);
        
        // Get the appropriate client for this provider
        ProviderStreamingClient client = clientsByProviderId.get(providerId);
        
        if (client == null) {
            log.error("No streaming client found for provider: {}", providerId);
            return Flux.error(new IllegalArgumentException("Unsupported provider: " + providerId));
        }
        
        // Check if the client supports this model
        if (!client.supportsModel(modelId)) {
            log.error("Provider {} does not support model: {}", providerId, modelId);
            return Flux.error(new IllegalArgumentException(
                    "Provider " + providerId + " does not support model: " + modelId));
        }
        
        // Stream the response
        return client.streamResponse(request)
                .onErrorResume(error -> {
                    log.error("Error streaming from provider: {}", providerId, error);
                    
                    // Create an error response
                    StreamingResponse errorResponse = StreamingResponse.builder()
                            .providerId(providerId)
                            .modelId(modelId)
                            .type(StreamingResponse.ResponseType.ERROR)
                            .error(StreamingResponse.ErrorInfo.builder()
                                    .code("streaming_error")
                                    .message(error.getMessage())
                                    .type(error.getClass().getSimpleName())
                                    .build())
                            .done(true)
                            .build();
                    
                    return Mono.just(errorResponse);
                });
    }
    
    /**
     * Get a list of all supported providers
     * @return List of provider IDs
     */
    public List<String> getSupportedProviders() {
        return List.copyOf(clientsByProviderId.keySet());
    }
    
    /**
     * Check if a provider is supported
     * @param providerId The provider ID to check
     * @return True if the provider is supported, false otherwise
     */
    public boolean isProviderSupported(String providerId) {
        return clientsByProviderId.containsKey(providerId);
    }
    
    /**
     * Get a list of supported models for a provider
     * @param providerId The provider ID
     * @return List of supported model IDs, or empty list if provider not supported
     */
    public List<String> getSupportedModelsForProvider(String providerId) {
        ProviderStreamingClient client = clientsByProviderId.get(providerId);
        if (client == null) {
            return List.of();
        }
        
        // This would typically come from a model registry or configuration
        // For now, we're returning a hardcoded list based on the provider
        switch (providerId) {
            case "openai":
                return List.of("gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo");
            case "claude":
                return List.of("claude-3-5-sonnet", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku");
            case "gemini":
                return List.of("gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro");
            default:
                return List.of();
        }
    }
}
