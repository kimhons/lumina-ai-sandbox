# Advanced Provider Integration Implementation Guide

This guide provides detailed implementation instructions for the Advanced Provider Integration component of Lumina AI.

## Overview

The Advanced Provider Integration system enables Lumina AI to seamlessly integrate with multiple AI providers, ensuring high-quality, robust, and powerful agentic AI capabilities.

## Implementation Steps

### 1. Set Up Project Structure

The Advanced Provider Integration follows a standard Spring Boot microservice architecture with the following structure:

```
lumina-ai/microservices/provider-service/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── ai/
│   │   │       └── lumina/
│   │   │           └── provider/
│   │   │               ├── model/
│   │   │               ├── repository/
│   │   │               ├── service/
│   │   │               ├── controller/
│   │   │               ├── config/
│   │   │               ├── exception/
│   │   │               └── util/
│   │   └── resources/
│   │       └── application.yml
│   └── test/
│       └── java/
│           └── ai/
│               └── lumina/
│                   └── provider/
│                       └── test/
└── pom.xml
```

### 2. Implement Model Classes

The core model classes represent the domain entities:

- `Provider`: Represents an AI provider (OpenAI, Anthropic, Google AI, etc.)
- `Model`: Represents an AI model with its capabilities and parameters
- `ProviderRequest`: Represents a request to an AI provider
- `Tool`: Represents a tool that can be used by AI agents
- `ToolExecution`: Represents the execution of a tool

Each model class should include appropriate JPA annotations for persistence.

### 3. Implement Repository Interfaces

Create repository interfaces for each model class using Spring Data JPA:

- `ProviderRepository`
- `ModelRepository`
- `ProviderRequestRepository`
- `ToolRepository`
- `ToolExecutionRepository`

These repositories should extend `JpaRepository` and include custom query methods as needed.

### 4. Implement Service Classes

Create service classes that implement the business logic:

- `ProviderService`: Manages provider registration and configuration
- `ModelService`: Manages model selection and optimization
- `ProviderRequestService`: Manages requests to providers
- `ToolService`: Manages tool registration and discovery
- `ToolExecutionService`: Manages tool execution
- `ProviderIntegrationService`: Provides a unified interface for provider integration

Each service should include methods for CRUD operations and business-specific operations.

### 5. Implement Controller Classes

Create REST controllers that expose the service functionality:

- `ProviderController`: Exposes provider operations
- `ModelController`: Exposes model operations
- `ProviderRequestController`: Exposes request operations
- `ToolController`: Exposes tool operations
- `ToolExecutionController`: Exposes tool execution operations
- `ProviderIntegrationController`: Exposes the unified integration interface

Each controller should include appropriate request mapping, validation, and error handling.

### 6. Implement Provider-Specific Adapters

Create adapter classes for each supported provider:

- `OpenAIAdapter`: Adapter for OpenAI
- `AnthropicAdapter`: Adapter for Anthropic
- `GoogleAIAdapter`: Adapter for Google AI
- `HuggingFaceAdapter`: Adapter for Hugging Face
- `CohereAdapter`: Adapter for Cohere
- `CustomModelAdapter`: Adapter for custom models

Each adapter should implement a common interface to ensure consistent behavior.

### 7. Implement Tool Framework

Create a framework for tool definition and execution:

- `ToolDefinition`: Defines a tool's capabilities and parameters
- `ToolExecutor`: Executes tools based on their definitions
- `ToolRegistry`: Registers and discovers tools
- `ToolResult`: Represents the result of a tool execution

### 8. Implement Smart Routing

Create a routing system that intelligently selects the most appropriate provider and model for each task:

- `ProviderRouter`: Routes requests to the appropriate provider
- `ModelSelector`: Selects the most appropriate model for a task
- `RoutingStrategy`: Defines routing strategies (cost, performance, availability)
- `RoutingDecision`: Represents a routing decision

### 9. Implement Resilience Features

Create components that ensure resilience and fault tolerance:

- `CircuitBreaker`: Prevents cascading failures
- `RateLimiter`: Prevents quota exhaustion
- `RetryHandler`: Handles retries with exponential backoff
- `FallbackProvider`: Provides fallback options when a provider fails

### 10. Configure Application

Create an application configuration file (`application.yml`) that includes:

- Database configuration
- Server configuration
- Logging configuration
- Security configuration
- Provider-specific configuration
- Custom application properties

### 11. Implement Integration Tests

Create integration tests that verify the functionality of the system:

- Repository tests
- Service tests
- Controller tests
- End-to-end tests
- Provider-specific tests

### 12. Deployment

Create deployment artifacts:

- Dockerfile
- Docker Compose configuration
- Kubernetes manifests (if applicable)

## Implementation Details

### Model Class Example: Provider.java

```java
@Entity
@Table(name = "providers")
public class Provider {
    @Id
    private String id;
    
    @Column(nullable = false, unique = true)
    private String name;
    
    @Column(nullable = false)
    private String description;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ProviderType type;
    
    @Column(nullable = false)
    private String baseUrl;
    
    @Column(nullable = false)
    private boolean enabled;
    
    @Column(nullable = false)
    private int priority;
    
    @ElementCollection
    @CollectionTable(name = "provider_capabilities", joinColumns = @JoinColumn(name = "provider_id"))
    @Column(name = "capability")
    private Set<String> capabilities = new HashSet<>();
    
    @ElementCollection
    @CollectionTable(name = "provider_api_keys", joinColumns = @JoinColumn(name = "provider_id"))
    @MapKeyColumn(name = "key_name")
    @Column(name = "key_value")
    private Map<String, String> apiKeys = new HashMap<>();
    
    @Column(nullable = false)
    private LocalDateTime createdAt;
    
    @Column
    private LocalDateTime updatedAt;
    
    // Getters, setters, and other methods
}
```

### Repository Interface Example: ProviderRepository.java

```java
@Repository
public interface ProviderRepository extends JpaRepository<Provider, String> {
    Optional<Provider> findByName(String name);
    List<Provider> findByType(ProviderType type);
    List<Provider> findByEnabledTrue();
    List<Provider> findByEnabledTrueOrderByPriorityDesc();
    List<Provider> findByCapabilitiesContaining(String capability);
    List<Provider> findByEnabledTrueAndCapabilitiesContaining(String capability);
}
```

### Service Class Example: ProviderIntegrationService.java

```java
@Service
public class ProviderIntegrationService {
    private final ProviderService providerService;
    private final ModelService modelService;
    private final ProviderRequestService requestService;
    private final ToolService toolService;
    private final ToolExecutionService toolExecutionService;
    private final Map<ProviderType, ProviderAdapter> providerAdapters;
    private final ProviderRouter providerRouter;
    
    @Autowired
    public ProviderIntegrationService(
            ProviderService providerService,
            ModelService modelService,
            ProviderRequestService requestService,
            ToolService toolService,
            ToolExecutionService toolExecutionService,
            Map<ProviderType, ProviderAdapter> providerAdapters,
            ProviderRouter providerRouter) {
        this.providerService = providerService;
        this.modelService = modelService;
        this.requestService = requestService;
        this.toolService = toolService;
        this.toolExecutionService = toolExecutionService;
        this.providerAdapters = providerAdapters;
        this.providerRouter = providerRouter;
    }
    
    public ChatResponse sendChatRequest(ChatRequest chatRequest) {
        // Determine the best provider and model for this request
        RoutingDecision routingDecision = providerRouter.routeChatRequest(chatRequest);
        Provider provider = routingDecision.getProvider();
        Model model = routingDecision.getModel();
        
        // Create a provider request
        ProviderRequest providerRequest = new ProviderRequest();
        providerRequest.setId(UUID.randomUUID().toString());
        providerRequest.setProviderId(provider.getId());
        providerRequest.setModelId(model.getId());
        providerRequest.setUserId(chatRequest.getUserId());
        providerRequest.setRequestType(RequestType.CHAT);
        providerRequest.setContent(chatRequest.getMessages());
        providerRequest.setParameters(chatRequest.getParameters());
        providerRequest.setCreatedAt(LocalDateTime.now());
        
        // Save the request
        providerRequest = requestService.createRequest(providerRequest);
        
        try {
            // Get the appropriate adapter
            ProviderAdapter adapter = providerAdapters.get(provider.getType());
            
            // Send the request to the provider
            ChatResponse response = adapter.sendChatRequest(provider, model, chatRequest);
            
            // Update the request with the response
            providerRequest.setResponse(response);
            providerRequest.setCompletedAt(LocalDateTime.now());
            providerRequest.setStatus(RequestStatus.COMPLETED);
            requestService.updateRequest(providerRequest.getId(), providerRequest);
            
            return response;
        } catch (Exception e) {
            // Handle the error
            providerRequest.setError(e.getMessage());
            providerRequest.setCompletedAt(LocalDateTime.now());
            providerRequest.setStatus(RequestStatus.FAILED);
            requestService.updateRequest(providerRequest.getId(), providerRequest);
            
            // Try fallback if available
            if (chatRequest.isAllowFallback()) {
                return handleFallback(chatRequest, provider, e);
            }
            
            throw new ProviderIntegrationException("Failed to send chat request", e);
        }
    }
    
    private ChatResponse handleFallback(ChatRequest chatRequest, Provider failedProvider, Exception originalError) {
        try {
            // Get fallback routing decision
            RoutingDecision fallbackDecision = providerRouter.routeChatRequestWithFallback(chatRequest, failedProvider);
            
            if (fallbackDecision != null) {
                // Create a new request with fallback information
                ChatRequest fallbackRequest = new ChatRequest(chatRequest);
                fallbackRequest.setFallbackFromProvider(failedProvider.getId());
                fallbackRequest.setFallbackReason(originalError.getMessage());
                
                // Send the request to the fallback provider
                return sendChatRequest(fallbackRequest);
            }
        } catch (Exception e) {
            // Log fallback error but throw original error
            log.error("Fallback also failed", e);
        }
        
        throw new ProviderIntegrationException("Failed to send chat request and fallback also failed", originalError);
    }
    
    // Other methods for different request types (completion, embedding, etc.)
    
    public ToolExecutionResult executeToolWithAI(String toolId, Map<String, Object> parameters, String userId) {
        // Get the tool
        Tool tool = toolService.getTool(toolId);
        
        // Create a tool execution
        ToolExecution execution = new ToolExecution();
        execution.setId(UUID.randomUUID().toString());
        execution.setToolId(toolId);
        execution.setUserId(userId);
        execution.setParameters(parameters);
        execution.setStatus(ExecutionStatus.PENDING);
        execution.setCreatedAt(LocalDateTime.now());
        
        // Save the execution
        execution = toolExecutionService.createExecution(execution);
        
        try {
            // Execute the tool
            ToolExecutionResult result = toolExecutionService.executeToolWithAI(tool, parameters, userId);
            
            // Update the execution with the result
            execution.setResult(result);
            execution.setCompletedAt(LocalDateTime.now());
            execution.setStatus(ExecutionStatus.COMPLETED);
            toolExecutionService.updateExecution(execution.getId(), execution);
            
            return result;
        } catch (Exception e) {
            // Handle the error
            execution.setError(e.getMessage());
            execution.setCompletedAt(LocalDateTime.now());
            execution.setStatus(ExecutionStatus.FAILED);
            toolExecutionService.updateExecution(execution.getId(), execution);
            
            throw new ToolExecutionException("Failed to execute tool", e);
        }
    }
}
```

### Controller Class Example: ProviderIntegrationController.java

```java
@RestController
@RequestMapping("/api/integration")
public class ProviderIntegrationController {
    private final ProviderIntegrationService integrationService;
    
    @Autowired
    public ProviderIntegrationController(ProviderIntegrationService integrationService) {
        this.integrationService = integrationService;
    }
    
    @PostMapping("/chat")
    public ResponseEntity<ChatResponse> sendChatRequest(@RequestBody @Valid ChatRequest chatRequest) {
        ChatResponse response = integrationService.sendChatRequest(chatRequest);
        return new ResponseEntity<>(response, HttpStatus.OK);
    }
    
    @PostMapping("/completion")
    public ResponseEntity<CompletionResponse> sendCompletionRequest(
            @RequestBody @Valid CompletionRequest completionRequest) {
        CompletionResponse response = integrationService.sendCompletionRequest(completionRequest);
        return new ResponseEntity<>(response, HttpStatus.OK);
    }
    
    @PostMapping("/embedding")
    public ResponseEntity<EmbeddingResponse> sendEmbeddingRequest(
            @RequestBody @Valid EmbeddingRequest embeddingRequest) {
        EmbeddingResponse response = integrationService.sendEmbeddingRequest(embeddingRequest);
        return new ResponseEntity<>(response, HttpStatus.OK);
    }
    
    @PostMapping("/image")
    public ResponseEntity<ImageResponse> sendImageRequest(@RequestBody @Valid ImageRequest imageRequest) {
        ImageResponse response = integrationService.sendImageRequest(imageRequest);
        return new ResponseEntity<>(response, HttpStatus.OK);
    }
    
    @PostMapping("/audio")
    public ResponseEntity<AudioResponse> sendAudioRequest(@RequestBody @Valid AudioRequest audioRequest) {
        AudioResponse response = integrationService.sendAudioRequest(audioRequest);
        return new ResponseEntity<>(response, HttpStatus.OK);
    }
    
    @PostMapping("/tools/{toolId}/execute")
    public ResponseEntity<ToolExecutionResult> executeToolWithAI(
            @PathVariable String toolId,
            @RequestBody Map<String, Object> parameters,
            @RequestParam String userId) {
        ToolExecutionResult result = integrationService.executeToolWithAI(toolId, parameters, userId);
        return new ResponseEntity<>(result, HttpStatus.OK);
    }
}
```

### Provider Adapter Example: OpenAIAdapter.java

```java
@Component
public class OpenAIAdapter implements ProviderAdapter {
    private final RestTemplate restTemplate;
    
    @Autowired
    public OpenAIAdapter(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    
    @Override
    public ChatResponse sendChatRequest(Provider provider, Model model, ChatRequest chatRequest) {
        // Convert Lumina AI chat request to OpenAI format
        OpenAIChatRequest openAIRequest = convertToOpenAIRequest(chatRequest, model);
        
        // Set up headers with API key
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("Authorization", "Bearer " + provider.getApiKeys().get("openai"));
        
        // Create HTTP entity
        HttpEntity<OpenAIChatRequest> entity = new HttpEntity<>(openAIRequest, headers);
        
        // Send request to OpenAI
        ResponseEntity<OpenAIChatResponse> response = restTemplate.exchange(
                provider.getBaseUrl() + "/chat/completions",
                HttpMethod.POST,
                entity,
                OpenAIChatResponse.class);
        
        // Convert OpenAI response to Lumina AI format
        return convertFromOpenAIResponse(response.getBody(), model);
    }
    
    private OpenAIChatRequest convertToOpenAIRequest(ChatRequest chatRequest, Model model) {
        OpenAIChatRequest openAIRequest = new OpenAIChatRequest();
        openAIRequest.setModel(model.getProviderId());
        
        // Convert messages
        List<OpenAIChatMessage> messages = chatRequest.getMessages().stream()
                .map(this::convertMessage)
                .collect(Collectors.toList());
        openAIRequest.setMessages(messages);
        
        // Set parameters
        openAIRequest.setTemperature(
                chatRequest.getParameters().getOrDefault("temperature", 0.7));
        openAIRequest.setMaxTokens(
                (int) chatRequest.getParameters().getOrDefault("max_tokens", 1000));
        openAIRequest.setTopP(
                chatRequest.getParameters().getOrDefault("top_p", 1.0));
        openAIRequest.setFrequencyPenalty(
                chatRequest.getParameters().getOrDefault("frequency_penalty", 0.0));
        openAIRequest.setPresencePenalty(
                chatRequest.getParameters().getOrDefault("presence_penalty", 0.0));
        
        // Convert tools if present
        if (chatRequest.getTools() != null && !chatRequest.getTools().isEmpty()) {
            List<OpenAITool> tools = chatRequest.getTools().stream()
                    .map(this::convertTool)
                    .collect(Collectors.toList());
            openAIRequest.setTools(tools);
            
            if (chatRequest.getToolChoice() != null) {
                openAIRequest.setToolChoice(convertToolChoice(chatRequest.getToolChoice()));
            }
        }
        
        return openAIRequest;
    }
    
    private OpenAIChatMessage convertMessage(ChatMessage message) {
        OpenAIChatMessage openAIMessage = new OpenAIChatMessage();
        openAIMessage.setRole(message.getRole());
        openAIMessage.setContent(message.getContent());
        
        if (message.getToolCalls() != null && !message.getToolCalls().isEmpty()) {
            List<OpenAIToolCall> toolCalls = message.getToolCalls().stream()
                    .map(this::convertToolCall)
                    .collect(Collectors.toList());
            openAIMessage.setToolCalls(toolCalls);
        }
        
        if (message.getToolCallId() != null) {
            openAIMessage.setToolCallId(message.getToolCallId());
        }
        
        return openAIMessage;
    }
    
    private OpenAITool convertTool(Tool tool) {
        OpenAITool openAITool = new OpenAITool();
        openAITool.setType("function");
        
        OpenAIFunction function = new OpenAIFunction();
        function.setName(tool.getName());
        function.setDescription(tool.getDescription());
        
        // Convert parameters to JSON Schema
        Map<String, Object> parameters = new HashMap<>();
        parameters.put("type", "object");
        
        Map<String, Object> properties = new HashMap<>();
        List<String> required = new ArrayList<>();
        
        for (ToolParameter param : tool.getParameters()) {
            Map<String, Object> property = new HashMap<>();
            property.put("type", param.getType());
            property.put("description", param.getDescription());
            
            if (param.getEnum() != null && !param.getEnum().isEmpty()) {
                property.put("enum", param.getEnum());
            }
            
            properties.put(param.getName(), property);
            
            if (param.isRequired()) {
                required.add(param.getName());
            }
        }
        
        parameters.put("properties", properties);
        parameters.put("required", required);
        
        function.setParameters(parameters);
        openAITool.setFunction(function);
        
        return openAITool;
    }
    
    private Object convertToolChoice(String toolChoice) {
        if ("auto".equals(toolChoice)) {
            return "auto";
        } else if ("none".equals(toolChoice)) {
            return "none";
        } else {
            Map<String, Object> choice = new HashMap<>();
            Map<String, String> function = new HashMap<>();
            function.put("name", toolChoice);
            choice.put("type", "function");
            choice.put("function", function);
            return choice;
        }
    }
    
    private OpenAIToolCall convertToolCall(ToolCall toolCall) {
        OpenAIToolCall openAIToolCall = new OpenAIToolCall();
        openAIToolCall.setId(toolCall.getId());
        openAIToolCall.setType("function");
        
        OpenAIFunctionCall functionCall = new OpenAIFunctionCall();
        functionCall.setName(toolCall.getName());
        functionCall.setArguments(toolCall.getArguments());
        
        openAIToolCall.setFunction(functionCall);
        
        return openAIToolCall;
    }
    
    private ChatResponse convertFromOpenAIResponse(OpenAIChatResponse openAIResponse, Model model) {
        ChatResponse response = new ChatResponse();
        response.setProviderId(model.getProviderId());
        response.setModelId(model.getId());
        
        // Convert choices
        List<ChatResponseChoice> choices = openAIResponse.getChoices().stream()
                .map(this::convertChoice)
                .collect(Collectors.toList());
        response.setChoices(choices);
        
        // Set usage
        Map<String, Integer> usage = new HashMap<>();
        usage.put("prompt_tokens", openAIResponse.getUsage().getPromptTokens());
        usage.put("completion_tokens", openAIResponse.getUsage().getCompletionTokens());
        usage.put("total_tokens", openAIResponse.getUsage().getTotalTokens());
        response.setUsage(usage);
        
        return response;
    }
    
    private ChatResponseChoice convertChoice(OpenAIChatChoice openAIChoice) {
        ChatResponseChoice choice = new ChatResponseChoice();
        choice.setIndex(openAIChoice.getIndex());
        
        // Convert message
        ChatMessage message = new ChatMessage();
        message.setRole(openAIChoice.getMessage().getRole());
        message.setContent(openAIChoice.getMessage().getContent());
        
        // Convert tool calls if present
        if (openAIChoice.getMessage().getToolCalls() != null) {
            List<ToolCall> toolCalls = openAIChoice.getMessage().getToolCalls().stream()
                    .map(this::convertToolCallFromResponse)
                    .collect(Collectors.toList());
            message.setToolCalls(toolCalls);
        }
        
        choice.setMessage(message);
        choice.setFinishReason(openAIChoice.getFinishReason());
        
        return choice;
    }
    
    private ToolCall convertToolCallFromResponse(OpenAIToolCall openAIToolCall) {
        ToolCall toolCall = new ToolCall();
        toolCall.setId(openAIToolCall.getId());
        toolCall.setType(openAIToolCall.getType());
        toolCall.setName(openAIToolCall.getFunction().getName());
        toolCall.setArguments(openAIToolCall.getFunction().getArguments());
        
        return toolCall;
    }
    
    // Other methods for different request types (completion, embedding, etc.)
}
```

## Best Practices

1. **Provider Abstraction**: Abstract provider-specific details behind a common interface
2. **Resilience**: Implement circuit breakers, rate limiters, and retry mechanisms
3. **Fallback Mechanisms**: Provide fallback options when a provider fails
4. **Caching**: Cache responses to reduce costs and improve performance
5. **Monitoring**: Monitor provider health, performance, and costs
6. **Security**: Securely manage API keys and other credentials
7. **Testing**: Write comprehensive tests for all components, including provider-specific tests
8. **Documentation**: Document APIs using Swagger/OpenAPI

## Conclusion

Following this implementation guide will result in a robust, scalable Advanced Provider Integration system for Lumina AI that can seamlessly integrate with multiple AI providers, ensuring high-quality, robust, and powerful agentic AI capabilities.
