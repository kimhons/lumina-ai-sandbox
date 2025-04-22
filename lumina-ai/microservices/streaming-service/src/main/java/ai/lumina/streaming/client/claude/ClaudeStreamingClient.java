package ai.lumina.streaming.client.claude;

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
 * Claude-specific implementation of the ProviderStreamingClient interface.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class ClaudeStreamingClient implements ProviderStreamingClient {

    private final WebClient webClient;
    private static final String PROVIDER_ID = "claude";
    private static final List<String> SUPPORTED_MODELS = List.of(
            "claude-3-5-sonnet", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"
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
        log.info("Streaming request to Claude for model: {}", request.getModelId());
        
        Map<String, Object> claudeRequest = convertToClaudeRequest(request);
        
        return webClient.post()
                .uri("/v1/messages")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(claudeRequest)
                .retrieve()
                .bodyToFlux(Map.class)
                .map(response -> convertFromClaudeResponse(response, request))
                .doOnError(error -> log.error("Error streaming from Claude", error));
    }
    
    /**
     * Convert the unified StreamingRequest to Claude-specific request format
     */
    private Map<String, Object> convertToClaudeRequest(StreamingRequest request) {
        Map<String, Object> claudeRequest = new HashMap<>();
        
        // Add model
        claudeRequest.put("model", request.getModelId());
        
        // Convert messages
        List<Map<String, Object>> messages = request.getMessages().stream()
                .map(message -> {
                    Map<String, Object> claudeMessage = new HashMap<>();
                    
                    // Map roles (Claude uses "user", "assistant", and "system")
                    String role = message.getRole();
                    claudeMessage.put("role", role);
                    
                    // Handle content
                    claudeMessage.put("content", message.getContent());
                    
                    return claudeMessage;
                })
                .collect(Collectors.toList());
        
        claudeRequest.put("messages", messages);
        
        // Add streaming parameter
        claudeRequest.put("stream", request.isStream());
        
        // Add optional parameters if present
        if (request.getMaxTokens() != null) {
            claudeRequest.put("max_tokens", request.getMaxTokens());
        }
        
        if (request.getTemperature() != null) {
            claudeRequest.put("temperature", request.getTemperature());
        }
        
        if (request.getTopP() != null) {
            claudeRequest.put("top_p", request.getTopP());
        }
        
        // Add tool calling if present (Claude uses "tools" instead of "functions")
        if (request.getFunctions() != null && !request.getFunctions().isEmpty()) {
            List<Map<String, Object>> tools = request.getFunctions().stream()
                    .map(function -> {
                        Map<String, Object> tool = new HashMap<>();
                        Map<String, Object> functionInfo = new HashMap<>();
                        
                        functionInfo.put("name", function.getName());
                        functionInfo.put("description", function.getDescription());
                        functionInfo.put("parameters", function.getParameters());
                        
                        tool.put("function", functionInfo);
                        return tool;
                    })
                    .collect(Collectors.toList());
            
            claudeRequest.put("tools", tools);
        }
        
        // Add any additional parameters
        if (request.getAdditionalParams() != null) {
            claudeRequest.putAll(request.getAdditionalParams());
        }
        
        return claudeRequest;
    }
    
    /**
     * Convert the Claude-specific response to the unified StreamingResponse format
     */
    @SuppressWarnings("unchecked")
    private StreamingResponse convertFromClaudeResponse(Map<String, Object> claudeResponse, StreamingRequest request) {
        StreamingResponse.StreamingResponseBuilder responseBuilder = StreamingResponse.builder()
                .providerId(PROVIDER_ID)
                .modelId(request.getModelId());
        
        // Extract ID if present
        if (claudeResponse.containsKey("id")) {
            responseBuilder.id((String) claudeResponse.get("id"));
        }
        
        // Check if this is an error response
        if (claudeResponse.containsKey("error")) {
            Map<String, Object> error = (Map<String, Object>) claudeResponse.get("error");
            StreamingResponse.ErrorInfo errorInfo = StreamingResponse.ErrorInfo.builder()
                    .code((String) error.getOrDefault("type", "unknown"))
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
        
        // Extract content from delta or content
        if (claudeResponse.containsKey("delta")) {
            Map<String, Object> delta = (Map<String, Object>) claudeResponse.get("delta");
            
            if (delta.containsKey("text")) {
                String content = (String) delta.get("text");
                responseBuilder
                        .type(StreamingResponse.ResponseType.TEXT)
                        .content(content != null ? content : "");
            } else if (delta.containsKey("tool_use")) {
                Map<String, Object> toolUse = (Map<String, Object>) delta.get("tool_use");
                Map<String, Object> function = (Map<String, Object>) toolUse.get("function");
                
                StreamingResponse.FunctionCall call = StreamingResponse.FunctionCall.builder()
                        .name((String) function.get("name"))
                        .arguments((String) function.get("arguments"))
                        .build();
                
                responseBuilder
                        .type(StreamingResponse.ResponseType.FUNCTION_CALL)
                        .functionCall(call);
            }
        } else if (claudeResponse.containsKey("content")) {
            List<Map<String, Object>> contentList = (List<Map<String, Object>>) claudeResponse.get("content");
            if (!contentList.isEmpty()) {
                Map<String, Object> contentItem = contentList.get(0);
                if (contentItem.containsKey("text")) {
                    String content = (String) contentItem.get("text");
                    responseBuilder
                            .type(StreamingResponse.ResponseType.TEXT)
                            .content(content != null ? content : "");
                }
            }
        }
        
        // Check if this is the final chunk
        boolean done = false;
        if (claudeResponse.containsKey("stop_reason")) {
            String stopReason = (String) claudeResponse.get("stop_reason");
            done = stopReason != null && !stopReason.isEmpty();
        }
        responseBuilder.done(done);
        
        // Extract usage if present
        if (claudeResponse.containsKey("usage")) {
            Map<String, Integer> usage = (Map<String, Integer>) claudeResponse.get("usage");
            StreamingResponse.UsageInfo usageInfo = StreamingResponse.UsageInfo.builder()
                    .promptTokens(usage.get("input_tokens"))
                    .completionTokens(usage.get("output_tokens"))
                    .totalTokens(usage.containsKey("total_tokens") ? 
                            usage.get("total_tokens") : 
                            (usage.get("input_tokens") + usage.get("output_tokens")))
                    .build();
            
            responseBuilder.usage(usageInfo);
        }
        
        // Add the full response as additional data
        responseBuilder.additionalData(claudeResponse);
        
        return responseBuilder.build();
    }
}
