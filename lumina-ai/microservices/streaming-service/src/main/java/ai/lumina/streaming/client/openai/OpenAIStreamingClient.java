package ai.lumina.streaming.client.openai;

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
 * OpenAI-specific implementation of the ProviderStreamingClient interface.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class OpenAIStreamingClient implements ProviderStreamingClient {

    private final WebClient webClient;
    private static final String PROVIDER_ID = "openai";
    private static final List<String> SUPPORTED_MODELS = List.of(
            "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"
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
        log.info("Streaming request to OpenAI for model: {}", request.getModelId());
        
        Map<String, Object> openaiRequest = convertToOpenAIRequest(request);
        
        return webClient.post()
                .uri("/v1/chat/completions")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(openaiRequest)
                .retrieve()
                .bodyToFlux(Map.class)
                .map(response -> convertFromOpenAIResponse(response, request))
                .doOnError(error -> log.error("Error streaming from OpenAI", error));
    }
    
    /**
     * Convert the unified StreamingRequest to OpenAI-specific request format
     */
    private Map<String, Object> convertToOpenAIRequest(StreamingRequest request) {
        Map<String, Object> openaiRequest = new HashMap<>();
        
        // Add model
        openaiRequest.put("model", request.getModelId());
        
        // Convert messages
        List<Map<String, Object>> messages = request.getMessages().stream()
                .map(message -> {
                    Map<String, Object> openaiMessage = new HashMap<>();
                    openaiMessage.put("role", message.getRole());
                    openaiMessage.put("content", message.getContent());
                    
                    if (message.getName() != null) {
                        openaiMessage.put("name", message.getName());
                    }
                    
                    if (message.getFunctionCall() != null) {
                        Map<String, String> functionCall = new HashMap<>();
                        functionCall.put("name", message.getFunctionCall().getName());
                        functionCall.put("arguments", message.getFunctionCall().getArguments());
                        openaiMessage.put("function_call", functionCall);
                    }
                    
                    return openaiMessage;
                })
                .collect(Collectors.toList());
        
        openaiRequest.put("messages", messages);
        
        // Add streaming parameter
        openaiRequest.put("stream", request.isStream());
        
        // Add optional parameters if present
        if (request.getMaxTokens() != null) {
            openaiRequest.put("max_tokens", request.getMaxTokens());
        }
        
        if (request.getTemperature() != null) {
            openaiRequest.put("temperature", request.getTemperature());
        }
        
        if (request.getTopP() != null) {
            openaiRequest.put("top_p", request.getTopP());
        }
        
        // Add functions if present
        if (request.getFunctions() != null && !request.getFunctions().isEmpty()) {
            List<Map<String, Object>> functions = request.getFunctions().stream()
                    .map(function -> {
                        Map<String, Object> openaiFunction = new HashMap<>();
                        openaiFunction.put("name", function.getName());
                        openaiFunction.put("description", function.getDescription());
                        openaiFunction.put("parameters", function.getParameters());
                        return openaiFunction;
                    })
                    .collect(Collectors.toList());
            
            openaiRequest.put("functions", functions);
        }
        
        // Add any additional parameters
        if (request.getAdditionalParams() != null) {
            openaiRequest.putAll(request.getAdditionalParams());
        }
        
        return openaiRequest;
    }
    
    /**
     * Convert the OpenAI-specific response to the unified StreamingResponse format
     */
    @SuppressWarnings("unchecked")
    private StreamingResponse convertFromOpenAIResponse(Map<String, Object> openaiResponse, StreamingRequest request) {
        StreamingResponse.StreamingResponseBuilder responseBuilder = StreamingResponse.builder()
                .providerId(PROVIDER_ID)
                .modelId(request.getModelId());
        
        // Extract ID if present
        if (openaiResponse.containsKey("id")) {
            responseBuilder.id((String) openaiResponse.get("id"));
        }
        
        // Check if this is an error response
        if (openaiResponse.containsKey("error")) {
            Map<String, Object> error = (Map<String, Object>) openaiResponse.get("error");
            StreamingResponse.ErrorInfo errorInfo = StreamingResponse.ErrorInfo.builder()
                    .code((String) error.getOrDefault("code", "unknown"))
                    .message((String) error.getOrDefault("message", "Unknown error"))
                    .type((String) error.getOrDefault("type", "unknown"))
                    .details(error)
                    .build();
            
            return responseBuilder
                    .type(StreamingResponse.ResponseType.ERROR)
                    .error(errorInfo)
                    .done(true)
                    .build();
        }
        
        // Extract choices
        if (openaiResponse.containsKey("choices")) {
            List<Map<String, Object>> choices = (List<Map<String, Object>>) openaiResponse.get("choices");
            if (!choices.isEmpty()) {
                Map<String, Object> choice = choices.get(0);
                
                // Check if this is the final chunk
                boolean done = false;
                if (choice.containsKey("finish_reason")) {
                    String finishReason = (String) choice.get("finish_reason");
                    done = finishReason != null && !finishReason.isEmpty();
                }
                
                // Extract delta or message
                Map<String, Object> delta = (Map<String, Object>) choice.getOrDefault("delta", 
                                           choice.getOrDefault("message", new HashMap<>()));
                
                // Check for function call
                if (delta.containsKey("function_call")) {
                    Map<String, String> functionCall = (Map<String, String>) delta.get("function_call");
                    StreamingResponse.FunctionCall call = StreamingResponse.FunctionCall.builder()
                            .name(functionCall.getOrDefault("name", ""))
                            .arguments(functionCall.getOrDefault("arguments", "{}"))
                            .build();
                    
                    responseBuilder
                            .type(StreamingResponse.ResponseType.FUNCTION_CALL)
                            .functionCall(call);
                } else if (delta.containsKey("content")) {
                    // Extract content
                    String content = (String) delta.get("content");
                    responseBuilder
                            .type(StreamingResponse.ResponseType.TEXT)
                            .content(content != null ? content : "");
                }
                
                responseBuilder.done(done);
            }
        }
        
        // Extract usage if present
        if (openaiResponse.containsKey("usage")) {
            Map<String, Integer> usage = (Map<String, Integer>) openaiResponse.get("usage");
            StreamingResponse.UsageInfo usageInfo = StreamingResponse.UsageInfo.builder()
                    .promptTokens(usage.get("prompt_tokens"))
                    .completionTokens(usage.get("completion_tokens"))
                    .totalTokens(usage.get("total_tokens"))
                    .build();
            
            responseBuilder.usage(usageInfo);
        }
        
        // Add the full response as additional data
        responseBuilder.additionalData(openaiResponse);
        
        return responseBuilder.build();
    }
}
