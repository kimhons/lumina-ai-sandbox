package ai.lumina.streaming.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * Represents a unified streaming response that can be received from any AI provider.
 * This model abstracts away provider-specific response formats.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StreamingResponse {
    
    /**
     * The provider ID that generated this response
     */
    private String providerId;
    
    /**
     * The model ID used for this response
     */
    private String modelId;
    
    /**
     * A unique identifier for this response
     */
    private String id;
    
    /**
     * The type of the response (e.g., "text", "function_call", "error")
     */
    private ResponseType type;
    
    /**
     * The content of the response, if type is "text"
     */
    private String content;
    
    /**
     * Function call information, if type is "function_call"
     */
    private FunctionCall functionCall;
    
    /**
     * Error information, if type is "error"
     */
    private ErrorInfo error;
    
    /**
     * Whether this is the final chunk in a streaming response
     */
    private boolean done;
    
    /**
     * Usage statistics for the response
     */
    private UsageInfo usage;
    
    /**
     * Additional provider-specific response data
     */
    private Map<String, Object> additionalData;
    
    /**
     * Represents the type of response
     */
    public enum ResponseType {
        TEXT,
        FUNCTION_CALL,
        ERROR
    }
    
    /**
     * Represents a function call in the response
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class FunctionCall {
        /**
         * The name of the function to call
         */
        private String name;
        
        /**
         * The arguments to pass to the function, as a JSON string
         */
        private String arguments;
    }
    
    /**
     * Represents error information
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ErrorInfo {
        /**
         * The error code
         */
        private String code;
        
        /**
         * The error message
         */
        private String message;
        
        /**
         * The type of error
         */
        private String type;
        
        /**
         * Additional error details
         */
        private Map<String, Object> details;
    }
    
    /**
     * Represents usage statistics
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class UsageInfo {
        /**
         * The number of prompt tokens used
         */
        private Integer promptTokens;
        
        /**
         * The number of completion tokens used
         */
        private Integer completionTokens;
        
        /**
         * The total number of tokens used
         */
        private Integer totalTokens;
    }
}
