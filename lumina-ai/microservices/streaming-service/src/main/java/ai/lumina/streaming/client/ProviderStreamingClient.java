package ai.lumina.streaming.client;

import ai.lumina.streaming.model.StreamingRequest;
import ai.lumina.streaming.model.StreamingResponse;
import reactor.core.publisher.Flux;

/**
 * Interface for provider-specific streaming clients.
 * Each AI provider implementation will implement this interface.
 */
public interface ProviderStreamingClient {

    /**
     * Get the provider ID that this client supports
     * @return The provider ID
     */
    String getProviderId();
    
    /**
     * Check if this client supports the specified model
     * @param modelId The model ID to check
     * @return True if the model is supported, false otherwise
     */
    boolean supportsModel(String modelId);
    
    /**
     * Stream a response from the AI provider
     * @param request The unified streaming request
     * @return A Flux of streaming response chunks
     */
    Flux<StreamingResponse> streamResponse(StreamingRequest request);
}
