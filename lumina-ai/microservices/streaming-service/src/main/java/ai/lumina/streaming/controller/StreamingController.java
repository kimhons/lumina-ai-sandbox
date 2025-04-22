package ai.lumina.streaming.controller;

import ai.lumina.streaming.model.StreamingRequest;
import ai.lumina.streaming.model.StreamingResponse;
import ai.lumina.streaming.service.StreamingManager;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/streaming")
@RequiredArgsConstructor
@Slf4j
public class StreamingController {

    private final StreamingManager streamingManager;

    /**
     * Stream a response from an AI provider
     * @param request The unified streaming request
     * @return A stream of response chunks
     */
    @PostMapping(produces = MediaType.APPLICATION_NDJSON_VALUE)
    public Flux<StreamingResponse> streamResponse(@RequestBody StreamingRequest request) {
        log.info("Received streaming request for provider: {}, model: {}", 
                request.getProviderId(), request.getModelId());
        return streamingManager.streamResponse(request);
    }
    
    /**
     * Get a list of supported providers
     * @return List of provider IDs
     */
    @GetMapping("/providers")
    public List<String> getSupportedProviders() {
        return streamingManager.getSupportedProviders();
    }
    
    /**
     * Check if a provider is supported
     * @param providerId The provider ID to check
     * @return Map with support status
     */
    @GetMapping("/providers/{providerId}")
    public Map<String, Boolean> isProviderSupported(@PathVariable String providerId) {
        boolean supported = streamingManager.isProviderSupported(providerId);
        return Map.of("supported", supported);
    }
    
    /**
     * Get a list of supported models for a provider
     * @param providerId The provider ID
     * @return List of supported model IDs
     */
    @GetMapping("/providers/{providerId}/models")
    public List<String> getSupportedModelsForProvider(@PathVariable String providerId) {
        return streamingManager.getSupportedModelsForProvider(providerId);
    }
}
