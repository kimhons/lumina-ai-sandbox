package ai.lumina.streaming.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * Represents a unified streaming request that can be sent to any AI provider.
 * This model abstracts away provider-specific request formats.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StreamingRequest {
    
    /**
     * The provider ID to route this request to
     */
    private String providerId;
    
    /**
     * The model ID to use for this request
     */
    private String modelId;
    
    /**
     * The prompt or messages to send to the AI provider
     */
    private List<Message> messages;
    
    /**
     * Whether to stream the response
     */
    private boolean stream;
    
    /**
     * Maximum number of tokens to generate
     */
    private Integer maxTokens;
    
    /**
     * Temperature for controlling randomness (0.0 to 2.0)
     */
    private Double temperature;
    
    /**
     * Top-p sampling parameter (0.0 to 1.0)
     */
    private Double topP;
    
    /**
     * Function calling definitions
     */
    private List<FunctionDefinition> functions;
    
    /**
     * Additional provider-specific parameters
     */
    private Map<String, Object> additionalParams;
    
    /**
     * Represents a message in a conversation
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Message {
        /**
         * The role of the message sender (e.g., "system", "user", "assistant")
         */
        private String role;
        
        /**
         * The content of the message
         */
        private String content;
        
        /**
         * Optional name of the sender
         */
        private String name;
        
        /**
         * Optional function call information
         */
        private FunctionCall functionCall;
    }
    
    /**
     * Represents a function call
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
     * Represents a function definition
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class FunctionDefinition {
        /**
         * The name of the function
         */
        private String name;
        
        /**
         * The description of the function
         */
        private String description;
        
        /**
         * The parameters of the function, as a JSON schema
         */
        private Map<String, Object> parameters;
    }
}
