package ai.lumina.streaming.client.gemini;

import ai.lumina.streaming.client.ProviderStreamingClient;
import ai.lumina.streaming.model.StreamingRequest;
import ai.lumina.streaming.model.StreamingResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Gemini-specific implementation of the ProviderStreamingClient interface.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class GeminiStreamingClient implements ProviderStreamingClient {

    private final WebClient webClient;
    private static final String PROVIDER_ID = "gemini";
    private static final List<String> SUPPORTED_MODELS = List.of(
            "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"
    );
    
    @Override
    public String getProviderId() {
        return PROVIDER_ID;
    }
    
    @Override
    public boolean supportsModel(String modelId) {
        return SUPPORTED_MODELS.contains(modelId);
    }
    
    @Override
    public Flux<StreamingResponse> streamResponse(StreamingRequest request) {
        log.info("Streaming request to Gemini for model: {}", request.getModelId());
        
        Map<String, Object> geminiRequest = convertToGeminiRequest(request);
        
        return webClient.post()
                .uri("/v1/models/" + request.getModelId() + ":streamGenerateContent")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(geminiRequest)
                .retrieve()
                .bodyToFlux(Map.class)
                .map(response -> convertFromGeminiResponse(response, request))
                .doOnError(error -> log.error("Error streaming from Gemini", error));
    }
    
    /**
     * Convert the unified StreamingRequest to Gemini-specific request format
     */
    private Map<String, Object> convertToGeminiRequest(StreamingRequest request) {
        Map<String, Object> geminiRequest = new HashMap<>();
        
        // Convert messages to Gemini's content format
        List<Map<String, Object>> contents = request.getMessages().stream()
                .map(message -> {
                    Map<String, Object> geminiContent = new HashMap<>();
                    
                    // Map roles (Gemini uses "user" and "model")
                    String role = "user";
                    if ("assistant".equals(message.getRole())) {
                        role = "model";
                    }
                    geminiContent.put("role", role);
                    
                    // Handle content
                    List<Map<String, String>> parts = List.of(
                            Map.of("text", message.getContent())
                    );
                    geminiContent.put("parts", parts);
                    
                    return geminiContent;
                })
                .collect(Collectors.toList());
        
        geminiRequest.put("contents", contents);
        
        // Add generation config
        Map<String, Object> generationConfig = new HashMap<>();
        
        if (request.getMaxTokens() != null) {
            generationConfig.put("maxOutputTokens", request.getMaxTokens());
        }
        
        if (request.getTemperature() != null) {
            generationConfig.put("temperature", request.getTemperature());
        }
        
        if (request.getTopP() != null) {
            generationConfig.put("topP", request.getTopP());
        }
        
        geminiRequest.put("generationConfig", generationConfig);
        
        // Add function calling if present
        if (request.getFunctions() != null && !request.getFunctions().isEmpty()) {
            List<Map<String, Object>> tools = request.getFunctions().stream()
                    .map(function -> {
                        Map<String, Object> tool = new HashMap<>();
                        Map<String, Object> functionDeclaration = new HashMap<>();
                        
                        functionDeclaration.put("name", function.getName());
                        functionDeclaration.put("description", function.getDescription());
                        functionDeclaration.put("parameters", function.getParameters());
                        
                        tool.put("functionDeclarations", List.of(functionDeclaration));
                        return tool;
                    })
                    .collect(Collectors.toList());
            
            geminiRequest.put("tools", tools);
        }
        
        // Add any additional parameters
        if (request.getAdditionalParams() != null) {
            geminiRequest.putAll(request.getAdditionalParams());
        }
        
        return geminiRequest;
    }
    
    /**
     * Convert the Gemini-specific response to the unified StreamingResponse format
     */
    @SuppressWarnings("unchecked")
    private StreamingResponse convertFromGeminiResponse(Map<String, Object> geminiResponse, StreamingRequest request) {
        StreamingResponse.StreamingResponseBuilder responseBuilder = StreamingResponse.builder()
                .providerId(PROVIDER_ID)
                .modelId(request.getModelId());
        
        // Check if this is an error response
        if (geminiResponse.containsKey("error")) {
            Map<String, Object> error = (Map<String, Object>) geminiResponse.get("error");
            StreamingResponse.ErrorInfo errorInfo = StreamingResponse.ErrorInfo.builder()
                    .code((String) error.getOrDefault("code", "unknown"))
                    .message((String) error.getOrDefault("message", "Unknown error"))
                    .type((String) error.getOrDefault("status", "unknown"))
                    .details(error)
                    .build();
            
            return responseBuilder
                    .type(StreamingResponse.ResponseType.ERROR)
                    .error(errorInfo)
                    .done(true)
                    .build();
        }
        
        // Extract content
        if (geminiResponse.containsKey("candidates")) {
            List<Map<String, Object>> candidates = (List<Map<String, Object>>) geminiResponse.get("candidates");
            if (!candidates.isEmpty()) {
                Map<String, Object> candidate = candidates.get(0);
                
                // Check if this is the final chunk
                boolean done = false;
                if (candidate.containsKey("finishReason")) {
                    String finishReason = (String) candidate.get("finishReason");
                    done = finishReason != null && !finishReason.isEmpty() && !"NOT_FINISHED".equals(finishReason);
                }
                
                if (candidate.containsKey("content")) {
                    Map<String, Object> content = (Map<String, Object>) candidate.get("content");
                    
                    if (content.containsKey("parts")) {
                        List<Map<String, Object>> parts = (List<Map<String, Object>>) content.get("parts");
                        if (!parts.isEmpty()) {
                            Map<String, Object> part = parts.get(0);
                            
                            if (part.containsKey("text")) {
                                String text = (String) part.get("text");
                                responseBuilder
                                        .type(StreamingResponse.ResponseType.TEXT)
                                        .content(text != null ? text : "");
                            } else if (part.containsKey("functionCall")) {
                                Map<String, Object> functionCall = (Map<String, Object>) part.get("functionCall");
                                
                                StreamingResponse.FunctionCall call = StreamingResponse.FunctionCall.builder()
                                        .name((String) functionCall.get("name"))
                                        .arguments((String) functionCall.get("args"))
                                        .build();
                                
                                responseBuilder
                                        .type(StreamingResponse.ResponseType.FUNCTION_CALL)
                                        .functionCall(call);
                            }
                        }
                    }
                }
                
                responseBuilder.done(done);
            }
        }
        
        // Extract usage if present
        if (geminiResponse.containsKey("usageMetadata")) {
            Map<String, Integer> usage = (Map<String, Integer>) geminiResponse.get("usageMetadata");
            StreamingResponse.UsageInfo usageInfo = StreamingResponse.UsageInfo.builder()
                    .promptTokens(usage.get("promptTokenCount"))
                    .completionTokens(usage.get("candidatesTokenCount"))
                    .totalTokens(usage.get("totalTokenCount"))
                    .build();
            
            responseBuilder.usage(usageInfo);
        }
        
        // Add the full response as additional data
        responseBuilder.additionalData(geminiResponse);
        
        return responseBuilder.build();
    }
}
