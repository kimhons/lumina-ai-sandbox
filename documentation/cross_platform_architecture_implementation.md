# Synergos AI: Cross-Platform Architecture Implementation

## Overview

This document outlines the implementation of the cross-platform architecture for Synergos AI, designed to serve both general users and PhD-level professionals solving complex problems. The architecture leverages React/Next.js for web applications and React Native for mobile applications, with a shared core to maximize code reuse and ensure consistent functionality across platforms.

## Architecture Components

### 1. Core Shared Layer

The core shared layer contains platform-agnostic logic and utilities that can be used across both web and mobile applications.

```
/shared
  /api
    - apiClient.js       # Base API client for all external services
    - aiProviders/       # Adapters for OpenAI, Claude, Gemini, DeepSeek, Grok
    - tools/             # Tool integrations for specialized tasks
  /state
    - store.js           # Global state management
    - reducers/          # State reducers by domain
    - actions/           # Action creators
  /utils
    - contextManager.js  # Context window tracking and management
    - tokenCounter.js    # Token counting for different models
    - formatters.js      # Shared formatting utilities
  /hooks
    - useAgent.js        # Hook for agent interactions
    - useTools.js        # Hook for tool access
    - useContext.js      # Hook for context management
  /types
    - index.ts           # TypeScript type definitions
```

### 2. Web Application (React/Next.js)

The web application is built with Next.js for server-side rendering, SEO benefits, and optimal performance.

```
/web
  /pages
    - index.js           # Landing page
    - dashboard.js       # Main dashboard
    - conversation.js    # Conversation interface
    - agents/            # Agent-specific pages
    - settings/          # Configuration pages
  /components
    /layout
      - Header.js        # Application header
      - Sidebar.js       # Navigation sidebar
      - Footer.js        # Application footer
    /conversation
      - MessageList.js   # Conversation message display
      - InputArea.js     # User input interface
      - ToolDisplay.js   # Tool usage visualization
    /agents
      - AgentCard.js     # Agent information card
      - AgentNetwork.js  # Agent relationship visualization
    /ui
      - Button.js        # Custom button component
      - Input.js         # Form input components
      - Card.js          # Content card component
  /styles
    - globals.css        # Global styles
    - theme.js           # Theme configuration
  /public
    - assets/            # Static assets
```

### 3. Mobile Application (React Native)

The mobile application is built with React Native for cross-platform mobile support.

```
/mobile
  /src
    /screens
      - HomeScreen.js    # Mobile home screen
      - ConversationScreen.js  # Conversation interface
      - AgentsScreen.js  # Agent management
      - SettingsScreen.js  # User settings
    /components
      /layout
        - Header.js      # Mobile header
        - TabBar.js      # Bottom navigation
      /conversation
        - MessageBubble.js  # Message display
        - InputBar.js    # Mobile input interface
        - ToolAccess.js  # Tool selection interface
      /ui
        - Button.js      # Mobile-optimized button
        - Input.js       # Mobile form inputs
        - Card.js        # Content card
    /navigation
      - AppNavigator.js  # Navigation configuration
    /styles
      - theme.js         # Mobile theme configuration
  /assets
    - images/            # Mobile-specific assets
```

### 4. Shared Component Library

A shared component library ensures consistent design and behavior across platforms.

```
/design-system
  /components
    - Button/            # Button implementations for web and mobile
    - Input/             # Input field implementations
    - Card/              # Card implementations
    - Typography/        # Text styling components
  /styles
    - colors.js          # Color definitions
    - typography.js      # Typography definitions
    - spacing.js         # Spacing system
  /icons
    - index.js           # Shared icon components
  /animations
    - transitions.js     # Shared animations
```

## Implementation Strategy

### Phase 1: Foundation Setup

1. **Project Initialization**
   - Set up monorepo structure with Yarn workspaces
   - Configure TypeScript for type safety
   - Set up ESLint and Prettier for code quality
   - Initialize Next.js project for web
   - Initialize React Native project for mobile

2. **Design System Implementation**
   - Implement color system based on UI design
   - Create typography components
   - Build basic UI components (Button, Input, Card)
   - Implement responsive layouts

3. **State Management Setup**
   - Configure Redux store with slices
   - Implement persistence layer
   - Create core reducers and actions
   - Set up middleware for async operations

### Phase 2: Platform-Specific Implementation

1. **Web Application**
   - Implement page routing with Next.js
   - Create responsive layouts for all screen sizes
   - Build conversation interface components
   - Implement agent visualization dashboard
   - Create settings and configuration pages

2. **Mobile Application**
   - Set up navigation with React Navigation
   - Implement mobile-optimized conversation interface
   - Create bottom tab navigation
   - Build gesture-based interactions
   - Optimize for different screen sizes

### Phase 3: Shared Logic Implementation

1. **API Integration**
   - Create placeholder services for AI providers
   - Implement token counting and context tracking
   - Build tool integration framework
   - Create error handling and retry logic

2. **Agent System**
   - Implement agent coordination logic
   - Create agent selection mechanism
   - Build context management system
   - Implement tool selection and execution

### Phase 4: Integration and Testing

1. **Integration**
   - Connect web and mobile frontends to shared logic
   - Implement platform-specific optimizations
   - Ensure consistent behavior across platforms

2. **Testing**
   - Create unit tests for shared components
   - Implement integration tests for key workflows
   - Set up end-to-end testing for critical paths
   - Perform cross-platform compatibility testing

## Code Examples

### Shared API Client

```javascript
// /shared/api/apiClient.js

class ApiClient {
  constructor(config) {
    this.baseUrl = config.baseUrl;
    this.apiKey = config.apiKey;
    this.timeout = config.timeout || 30000;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.apiKey}`,
      ...options.headers,
    };

    try {
      const response = await fetch(url, {
        method: options.method || 'GET',
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined,
        timeout: this.timeout,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }
}

export default ApiClient;
```

### AI Provider Adapter

```javascript
// /shared/api/aiProviders/openAiAdapter.js

import ApiClient from '../apiClient';

class OpenAiAdapter {
  constructor(apiKey) {
    this.client = new ApiClient({
      baseUrl: 'https://api.openai.com/v1',
      apiKey,
    });
    this.modelName = 'gpt-4o';
  }

  async generateCompletion(prompt, options = {}) {
    try {
      const response = await this.client.request('/chat/completions', {
        method: 'POST',
        body: {
          model: options.model || this.modelName,
          messages: [
            { role: 'system', content: options.systemPrompt || 'You are a helpful assistant.' },
            { role: 'user', content: prompt }
          ],
          temperature: options.temperature || 0.7,
          max_tokens: options.maxTokens || 1000,
        },
      });

      return {
        text: response.choices[0].message.content,
        usage: response.usage,
        model: response.model,
      };
    } catch (error) {
      console.error('OpenAI completion failed:', error);
      throw error;
    }
  }

  // Additional methods for streaming, function calling, etc.
}

export default OpenAiAdapter;
```

### Context Management

```javascript
// /shared/utils/contextManager.js

class ContextManager {
  constructor(options = {}) {
    this.maxTokens = options.maxTokens || 8192;
    this.currentTokens = 0;
    this.messages = [];
    this.tokenCounter = options.tokenCounter;
  }

  addMessage(message) {
    const tokenCount = this.tokenCounter.countTokens(message.content);
    
    // Check if adding this message would exceed the context window
    if (this.currentTokens + tokenCount > this.maxTokens) {
      this.pruneContext(tokenCount);
    }
    
    this.messages.push({
      ...message,
      tokenCount,
      timestamp: Date.now(),
    });
    
    this.currentTokens += tokenCount;
    return this.getContextUtilization();
  }

  pruneContext(requiredTokens) {
    // Remove oldest messages until we have enough space
    while (this.currentTokens + requiredTokens > this.maxTokens && this.messages.length > 0) {
      const removed = this.messages.shift();
      this.currentTokens -= removed.tokenCount;
    }
  }

  getContextUtilization() {
    return {
      used: this.currentTokens,
      total: this.maxTokens,
      percentage: (this.currentTokens / this.maxTokens) * 100,
    };
  }

  summarizeContext() {
    // Implementation for context summarization
  }

  clearContext() {
    this.messages = [];
    this.currentTokens = 0;
  }
}

export default ContextManager;
```

### React Hook for Agent Interaction

```javascript
// /shared/hooks/useAgent.js

import { useState, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { sendMessage, receiveMessage } from '../state/actions/conversationActions';

export function useAgent(agentId) {
  const dispatch = useDispatch();
  const [isLoading, setIsLoading] = useState(false);
  const conversation = useSelector(state => state.conversations.current);
  const agents = useSelector(state => state.agents.available);
  const agent = agents.find(a => a.id === agentId);

  const sendMessageToAgent = useCallback(async (message) => {
    if (!agent) {
      throw new Error(`Agent with ID ${agentId} not found`);
    }

    setIsLoading(true);
    dispatch(sendMessage({
      conversationId: conversation.id,
      content: message,
      sender: 'user',
    }));

    try {
      // In a real implementation, this would call the actual agent service
      const response = await agent.processMessage(message, conversation);
      
      dispatch(receiveMessage({
        conversationId: conversation.id,
        content: response.content,
        sender: agent.id,
        metadata: response.metadata,
      }));
      
      return response;
    } catch (error) {
      console.error('Agent processing failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [agent, agentId, conversation, dispatch]);

  return {
    agent,
    isLoading,
    sendMessage: sendMessageToAgent,
  };
}
```

### Web Component Example

```jsx
// /web/components/conversation/MessageList.js

import React, { useRef, useEffect } from 'react';
import { useSelector } from 'react-redux';
import Message from './Message';
import AgentIndicator from './AgentIndicator';
import ContextUtilization from './ContextUtilization';

const MessageList = ({ conversationId }) => {
  const messagesEndRef = useRef(null);
  const messages = useSelector(state => 
    state.conversations.byId[conversationId]?.messages || []
  );
  const contextUtilization = useSelector(state => 
    state.conversations.byId[conversationId]?.contextUtilization
  );

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  return (
    <div className="message-list-container">
      <ContextUtilization 
        used={contextUtilization?.used || 0}
        total={contextUtilization?.total || 8192}
      />
      
      <div className="message-list">
        {messages.map(message => (
          <div key={message.id} className="message-wrapper">
            {message.sender !== 'user' && (
              <AgentIndicator agentId={message.sender} />
            )}
            <Message 
              content={message.content}
              isUser={message.sender === 'user'}
              timestamp={message.timestamp}
              metadata={message.metadata}
            />
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessageList;
```

### Mobile Component Example

```jsx
// /mobile/src/components/conversation/MessageBubble.js

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useTheme } from '../../hooks/useTheme';
import AgentIcon from '../agents/AgentIcon';
import CodeBlock from './CodeBlock';
import ImagePreview from './ImagePreview';

const MessageBubble = ({ message, isUser, onLongPress }) => {
  const theme = useTheme();
  const { content, timestamp, sender, metadata } = message;
  
  // Determine if message contains code, images, or other special content
  const hasCode = content.includes('```');
  const hasImage = metadata?.attachments?.some(a => a.type === 'image');
  
  return (
    <TouchableOpacity
      onLongPress={() => onLongPress(message)}
      activeOpacity={0.8}
      style={styles.container}
    >
      {!isUser && (
        <View style={styles.agentIconContainer}>
          <AgentIcon agentId={sender} size={24} />
        </View>
      )}
      
      <View style={[
        styles.bubble,
        isUser ? styles.userBubble : styles.agentBubble,
        { backgroundColor: isUser ? theme.colors.primary : theme.colors.surface }
      ]}>
        {hasCode ? (
          <CodeBlock code={content} />
        ) : hasImage ? (
          <>
            <Text style={[
              styles.text,
              { color: isUser ? theme.colors.onPrimary : theme.colors.onSurface }
            ]}>
              {content}
            </Text>
            <ImagePreview attachments={metadata.attachments} />
          </>
        ) : (
          <Text style={[
            styles.text,
            { color: isUser ? theme.colors.onPrimary : theme.colors.onSurface }
          ]}>
            {content}
          </Text>
        )}
        
        <Text style={[
          styles.timestamp,
          { color: isUser ? theme.colors.onPrimaryMuted : theme.colors.onSurfaceMuted }
        ]}>
          {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    marginVertical: 8,
    paddingHorizontal: 16,
  },
  agentIconContainer: {
    marginRight: 8,
    alignSelf: 'flex-end',
  },
  bubble: {
    maxWidth: '80%',
    borderRadius: 16,
    padding: 12,
    elevation: 1,
  },
  userBubble: {
    alignSelf: 'flex-end',
    borderBottomRightRadius: 4,
    marginLeft: 'auto',
  },
  agentBubble: {
    alignSelf: 'flex-start',
    borderBottomLeftRadius: 4,
  },
  text: {
    fontSize: 16,
    lineHeight: 22,
  },
  timestamp: {
    fontSize: 12,
    alignSelf: 'flex-end',
    marginTop: 4,
  },
});

export default MessageBubble;
```

## Responsive Design Implementation

The architecture implements a responsive design approach that adapts to different screen sizes and device capabilities:

1. **Web Responsive Strategy**
   - Fluid layouts using CSS Grid and Flexbox
   - Breakpoints for mobile, tablet, desktop, and large desktop
   - Component-level media queries for fine-grained control
   - Progressive enhancement for advanced features

2. **Mobile Responsive Strategy**
   - React Native's Flexbox implementation for layouts
   - Device-specific adaptations using Dimensions API
   - Platform-specific components when necessary
   - Gesture-based interactions optimized for touch

## Cross-Platform Consistency

To ensure consistency across platforms:

1. **Shared Business Logic**
   - Core functionality implemented in shared modules
   - Platform-specific adapters for native features

2. **Design System**
   - Consistent color palette, typography, and spacing
   - Shared component specifications with platform-specific implementations
   - Common interaction patterns adapted for each platform

3. **State Management**
   - Centralized state management with Redux
   - Consistent data models across platforms
   - Shared action creators and reducers

## Next Steps

1. **Initial Setup**
   - Configure monorepo structure
   - Set up build processes for web and mobile
   - Implement core design system components

2. **Web Implementation**
   - Create responsive layouts for main screens
   - Implement conversation interface
   - Build agent visualization dashboard

3. **Mobile Implementation**
   - Develop mobile navigation structure
   - Create mobile-optimized conversation interface
   - Implement gesture-based interactions

4. **Shared Logic**
   - Implement placeholder services for AI providers
   - Create context management system
   - Build tool integration framework

This cross-platform architecture provides a solid foundation for Synergos AI, enabling us to deliver a consistent, high-quality experience across web and mobile platforms while maximizing code reuse and maintainability.
