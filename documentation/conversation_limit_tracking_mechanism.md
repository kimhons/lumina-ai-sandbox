# Conversation Limit Tracking Mechanism for Synergos AI

## Overview

This document outlines the detailed design of the conversation limit tracking mechanism for Synergos AI. This system will monitor and manage the conversation limits across different LLM providers (OpenAI, Anthropic, and Google) to ensure seamless operation and prevent unexpected failures due to context window limitations.

## Core Components

### 1. Token Counter Module

The Token Counter Module will track token usage across all interactions with LLM providers.

#### Implementation Details:

```python
class TokenCounter:
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.provider_counters = {
            "openai": {"input": 0, "output": 0},
            "anthropic": {"input": 0, "output": 0},
            "google": {"input": 0, "output": 0}
        }
        
    def count_tokens(self, text, provider, is_input=True):
        # Provider-specific tokenization logic
        if provider == "openai":
            token_count = self._count_openai_tokens(text)
        elif provider == "anthropic":
            token_count = self._count_anthropic_tokens(text)
        elif provider == "google":
            token_count = self._count_google_tokens(text)
        
        # Update counters
        if is_input:
            self.total_input_tokens += token_count
            self.provider_counters[provider]["input"] += token_count
        else:
            self.total_output_tokens += token_count
            self.provider_counters[provider]["output"] += token_count
            
        return token_count
    
    def _count_openai_tokens(self, text):
        # Use tiktoken for OpenAI tokenization
        import tiktoken
        encoder = tiktoken.encoding_for_model("gpt-4o")
        return len(encoder.encode(text))
    
    def _count_anthropic_tokens(self, text):
        # Anthropic-specific tokenization
        # Approximate using Claude's tokenization approach
        return len(text.split()) * 1.3  # Rough approximation
    
    def _count_google_tokens(self, text):
        # Google-specific tokenization
        # Approximate using Gemini's tokenization approach
        return len(text.split()) * 1.3  # Rough approximation
```

### 2. Context Window Manager

The Context Window Manager will track the current context size relative to each model's maximum capacity.

#### Implementation Details:

```python
class ContextWindowManager:
    def __init__(self):
        self.max_context_windows = {
            "gpt-4o": 128000,
            "claude-3-5-sonnet": 200000,
            "gemini-1-5-pro": 1000000
        }
        self.current_context_sizes = {
            "gpt-4o": 0,
            "claude-3-5-sonnet": 0,
            "gemini-1-5-pro": 0
        }
        self.token_counter = TokenCounter()
        
    def update_context_size(self, model, text, is_input=True):
        # Count tokens for the specific model
        if "gpt" in model:
            provider = "openai"
        elif "claude" in model:
            provider = "anthropic"
        elif "gemini" in model:
            provider = "google"
        
        token_count = self.token_counter.count_tokens(text, provider, is_input)
        self.current_context_sizes[model] += token_count
        
        # Return current percentage of context window used
        return self.get_context_percentage(model)
    
    def get_context_percentage(self, model):
        return (self.current_context_sizes[model] / self.max_context_windows[model]) * 100
    
    def is_approaching_limit(self, model, threshold=80):
        # Check if approaching the context window limit
        return self.get_context_percentage(model) >= threshold
    
    def is_at_limit(self, model, threshold=95):
        # Check if at or exceeding the context window limit
        return self.get_context_percentage(model) >= threshold
    
    def reset_context(self, model):
        # Reset context size for a specific model
        self.current_context_sizes[model] = 0
```

### 3. Notification System

The Notification System will alert users and system administrators when approaching context limits.

#### Implementation Details:

```python
class LimitNotificationSystem:
    def __init__(self, context_manager):
        self.context_manager = context_manager
        self.notification_thresholds = [50, 80, 90, 95]
        self.notified_thresholds = {model: set() for model in self.context_manager.max_context_windows.keys()}
        
    def check_and_notify(self, model, message_handler):
        percentage = self.context_manager.get_context_percentage(model)
        
        for threshold in self.notification_thresholds:
            if percentage >= threshold and threshold not in self.notified_thresholds[model]:
                self._send_notification(model, threshold, percentage, message_handler)
                self.notified_thresholds[model].add(threshold)
                
    def _send_notification(self, model, threshold, current_percentage, message_handler):
        if threshold >= 90:
            message = f"⚠️ WARNING: {model} is at {current_percentage:.1f}% of its context window capacity. Conversation may be truncated soon."
        elif threshold >= 80:
            message = f"⚠️ NOTICE: {model} is at {current_percentage:.1f}% of its context window capacity. Consider summarizing or starting a new conversation soon."
        else:
            message = f"ℹ️ INFO: {model} is at {current_percentage:.1f}% of its context window capacity."
            
        message_handler(message)
        
    def reset_notifications(self, model):
        self.notified_thresholds[model] = set()
```

### 4. Memory Management System

The Memory Management System will implement strategies to manage long conversations and prevent context overflow.

#### Implementation Details:

```python
class MemoryManager:
    def __init__(self, context_manager):
        self.context_manager = context_manager
        self.conversation_history = {model: [] for model in self.context_manager.max_context_windows.keys()}
        
    def add_exchange(self, model, user_message, ai_response):
        self.conversation_history[model].append({
            "user": user_message,
            "ai": ai_response,
            "timestamp": time.time()
        })
        
    def summarize_conversation(self, model, target_percentage=50):
        """Summarize conversation to reduce context size"""
        if not self.context_manager.is_approaching_limit(model):
            return None
            
        # Determine how much we need to summarize
        current_size = self.context_manager.current_context_sizes[model]
        max_size = self.context_manager.max_context_windows[model]
        target_size = max_size * (target_percentage / 100)
        
        # If we're below target already, no need to summarize
        if current_size <= target_size:
            return None
            
        # Prepare conversation for summarization
        conversation_text = self._format_conversation_for_summarization(model)
        
        # Use the model itself to summarize the conversation
        summary = self._generate_summary(model, conversation_text)
        
        # Reset context with the summary
        self.context_manager.reset_context(model)
        self.conversation_history[model] = [{
            "user": "Previous conversation summary",
            "ai": summary,
            "timestamp": time.time()
        }]
        
        return summary
        
    def _format_conversation_for_summarization(self, model):
        formatted_text = "Conversation history:\n\n"
        for exchange in self.conversation_history[model]:
            formatted_text += f"User: {exchange['user']}\n"
            formatted_text += f"AI: {exchange['ai']}\n\n"
        return formatted_text
        
    def _generate_summary(self, model, conversation_text):
        # This would use the appropriate LLM to generate a summary
        # Implementation depends on the specific API integration
        prompt = f"Please summarize the following conversation, preserving key information and context:\n\n{conversation_text}"
        
        # This is a placeholder - actual implementation would call the appropriate LLM
        if "gpt" in model:
            return self._summarize_with_openai(prompt)
        elif "claude" in model:
            return self._summarize_with_anthropic(prompt)
        elif "gemini" in model:
            return self._summarize_with_google(prompt)
    
    def prune_conversation(self, model, keep_last_n=5):
        """Prune conversation to keep only recent exchanges"""
        if len(self.conversation_history[model]) <= keep_last_n:
            return
            
        # Generate a summary of older messages
        older_messages = self.conversation_history[model][:-keep_last_n]
        older_text = self._format_conversation_for_summarization_subset(older_messages)
        summary = self._generate_summary(model, older_text)
        
        # Keep only recent messages plus a summary
        self.conversation_history[model] = [{
            "user": "Previous conversation summary",
            "ai": summary,
            "timestamp": time.time()
        }] + self.conversation_history[model][-keep_last_n:]
        
        # Recalculate context size
        self.context_manager.reset_context(model)
        for exchange in self.conversation_history[model]:
            self.context_manager.update_context_size(model, exchange["user"], is_input=True)
            self.context_manager.update_context_size(model, exchange["ai"], is_input=False)
```

### 5. Graceful Degradation Handler

The Graceful Degradation Handler will manage situations where context limits are reached.

#### Implementation Details:

```python
class GracefulDegradationHandler:
    def __init__(self, context_manager, memory_manager):
        self.context_manager = context_manager
        self.memory_manager = memory_manager
        
    def handle_limit_reached(self, model, message_handler):
        # First attempt: Summarize the conversation
        summary = self.memory_manager.summarize_conversation(model)
        if summary:
            message_handler(f"The conversation has been summarized to continue within {model}'s context limits. Key information has been preserved.")
            return True
            
        # Second attempt: Prune the conversation
        self.memory_manager.prune_conversation(model)
        if not self.context_manager.is_at_limit(model):
            message_handler(f"Some older parts of the conversation have been removed to continue within {model}'s context limits.")
            return True
            
        # Last resort: Switch to a model with larger context window
        alternative_model = self._find_alternative_model(model)
        if alternative_model:
            message_handler(f"Switching from {model} to {alternative_model} to accommodate the conversation length.")
            return alternative_model
            
        # If all else fails, inform the user that a new conversation is needed
        message_handler(f"⚠️ {model} has reached its context limit. Please start a new conversation to continue.")
        return False
        
    def _find_alternative_model(self, current_model):
        # Find a model with a larger context window
        current_max = self.context_manager.max_context_windows[current_model]
        
        alternatives = {
            model: max_size for model, max_size in self.context_manager.max_context_windows.items()
            if max_size > current_max
        }
        
        if not alternatives:
            return None
            
        # Return the model with the largest context window
        return max(alternatives.items(), key=lambda x: x[1])[0]
```

## Integration with Synergos AI

### Central Orchestration Agent Integration

The conversation limit tracking mechanism will be integrated with the Central Orchestration Agent to monitor all interactions across the system.

```python
class SynergosOrchestrator:
    def __init__(self):
        self.context_manager = ContextWindowManager()
        self.memory_manager = MemoryManager(self.context_manager)
        self.notification_system = LimitNotificationSystem(self.context_manager)
        self.degradation_handler = GracefulDegradationHandler(self.context_manager, self.memory_manager)
        
        # Initialize specialized agents
        self.research_agent = ResearchAgent()
        self.content_agent = ContentAgent()
        self.data_agent = DataAgent()
        self.code_agent = CodeAgent()
        
        # Map agents to their primary models
        self.agent_models = {
            "orchestrator": "gpt-4o",
            "research": "claude-3-5-sonnet",
            "content": "claude-3-5-sonnet",
            "data": "gemini-1-5-pro",
            "code": "gpt-4o"
        }
        
    def process_message(self, user_message, message_handler):
        # Update context for orchestrator
        orchestrator_model = self.agent_models["orchestrator"]
        self.context_manager.update_context_size(orchestrator_model, user_message)
        
        # Check for approaching limits
        self.notification_system.check_and_notify(orchestrator_model, message_handler)
        
        # Handle limit reached scenario
        if self.context_manager.is_at_limit(orchestrator_model):
            result = self.degradation_handler.handle_limit_reached(orchestrator_model, message_handler)
            if not result:
                return "Context limit reached. Please start a new conversation."
            elif isinstance(result, str):  # Alternative model suggested
                orchestrator_model = result
                
        # Determine which specialized agent should handle the request
        agent_type = self._route_to_appropriate_agent(user_message)
        agent_model = self.agent_models[agent_type]
        
        # Check if the specialized agent is approaching limits
        self.context_manager.update_context_size(agent_model, user_message)
        self.notification_system.check_and_notify(agent_model, message_handler)
        
        # Handle limit reached for specialized agent
        if self.context_manager.is_at_limit(agent_model):
            result = self.degradation_handler.handle_limit_reached(agent_model, message_handler)
            if not result:
                return "Context limit reached for specialized agent. Please start a new conversation."
            elif isinstance(result, str):  # Alternative model suggested
                agent_model = result
                
        # Process the message with the appropriate agent
        response = self._process_with_agent(agent_type, user_message)
        
        # Update context with the response
        self.context_manager.update_context_size(orchestrator_model, response, is_input=False)
        self.context_manager.update_context_size(agent_model, response, is_input=False)
        
        # Store the exchange in memory
        self.memory_manager.add_exchange(orchestrator_model, user_message, response)
        self.memory_manager.add_exchange(agent_model, user_message, response)
        
        return response
        
    def _route_to_appropriate_agent(self, message):
        # Logic to determine which agent should handle the message
        # This would be implemented based on message content analysis
        pass
        
    def _process_with_agent(self, agent_type, message):
        # Route the message to the appropriate agent
        if agent_type == "research":
            return self.research_agent.process(message)
        elif agent_type == "content":
            return self.content_agent.process(message)
        elif agent_type == "data":
            return self.data_agent.process(message)
        elif agent_type == "code":
            return self.code_agent.process(message)
        else:
            # Default to orchestrator handling
            return self._process_with_orchestrator(message)
            
    def _process_with_orchestrator(self, message):
        # Process the message with the orchestrator's model
        pass
```

## User Interface Integration

The conversation limit tracking mechanism will be integrated into the user interface to provide transparent feedback to users.

### Visual Indicators

1. **Context Usage Meter**: A visual progress bar showing the percentage of context window used for the current conversation.

2. **Model Indicator**: Display which model is currently being used for each response.

3. **Status Messages**: Non-intrusive status messages when approaching context limits.

### User Controls

1. **Manual Summarize Button**: Allow users to manually trigger conversation summarization.

2. **New Conversation Button**: Clearly visible option to start a new conversation when needed.

3. **Model Selection**: Allow users to manually switch between models with different context capacities.

## Implementation in DataStax Langflow

In Langflow, the conversation limit tracking mechanism will be implemented as a custom component that can be integrated into the workflow.

```
1. Create a custom "Context Tracker" component in Langflow
2. Add input nodes for user messages and model responses
3. Add output nodes for notifications and context status
4. Connect the component between the user input and LLM nodes
5. Add a feedback loop to update the context tracker after each response
```

## Testing Strategy

To ensure the conversation limit tracking mechanism works correctly, we will implement the following testing strategy:

1. **Unit Tests**: Test each component (TokenCounter, ContextWindowManager, etc.) in isolation.

2. **Integration Tests**: Test the interaction between components.

3. **Simulation Tests**: Simulate long conversations to trigger limit warnings and actions.

4. **Edge Case Tests**: Test scenarios like extremely long inputs, rapid message sequences, etc.

5. **User Experience Tests**: Gather feedback on the notification system and degradation handling.

## Deployment Plan

The conversation limit tracking mechanism will be deployed in phases:

1. **Phase 1**: Implement basic token counting and context tracking.

2. **Phase 2**: Add notification system and visual indicators.

3. **Phase 3**: Implement memory management (summarization and pruning).

4. **Phase 4**: Add graceful degradation handling.

5. **Phase 5**: Integrate with all specialized agents and refine based on user feedback.

## Conclusion

This conversation limit tracking mechanism provides a comprehensive solution for monitoring and managing context limits across different LLM providers in Synergos AI. By implementing proactive notifications, intelligent memory management, and graceful degradation strategies, we can ensure a seamless user experience even as conversations approach the inherent limits of the underlying models.

The system is designed to be transparent to users, providing clear information about context usage and taking appropriate actions to extend conversations when possible. This approach aligns with our goal of creating a powerful agentic system that can handle complex, multi-turn interactions while gracefully managing the technical limitations of current LLM technology.
