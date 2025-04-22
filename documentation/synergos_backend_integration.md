# Synergos AI: Backend Integration

## Overview

This document outlines the integration of the Synergos AI backend with the cross-platform frontend architecture. The backend integration connects our multi-agent system (Central Orchestration Agent, Research Agent, Content Agent, Data Agent, and Code Agent) with the web and mobile applications through a unified API layer.

## Integration Architecture

### 1. Backend Service Layer

The backend service layer provides the core AI functionality and coordinates between specialized agents.

```
/backend
  /services
    - orchestrationService.js    # Central coordination service
    - researchService.js         # Research agent service
    - contentService.js          # Content creation service
    - dataService.js             # Data analysis service
    - codeService.js             # Code generation service
  /models
    - conversation.js            # Conversation data model
    - agent.js                   # Agent configuration model
    - user.js                    # User profile model
    - tool.js                    # Tool definition model
  /utils
    - agentSelector.js           # Logic for selecting appropriate agent
    - contextManager.js          # Context window management
    - tokenCounter.js            # Token counting for different models
    - promptTemplates.js         # Reusable prompt templates
  /config
    - aiProviders.js             # AI provider configurations
    - serviceConfig.js           # Service configurations
```

### 2. API Gateway

The API Gateway provides a unified interface for frontend applications to interact with the backend services.

```
/api
  /routes
    - conversations.js           # Conversation management endpoints
    - agents.js                  # Agent configuration endpoints
    - tools.js                   # Tool access endpoints
    - users.js                   # User management endpoints
  /middleware
    - auth.js                    # Authentication middleware
    - rateLimit.js               # Rate limiting middleware
    - errorHandler.js            # Error handling middleware
  /controllers
    - conversationController.js  # Conversation logic
    - agentController.js         # Agent management logic
    - toolController.js          # Tool execution logic
    - userController.js          # User management logic
  /websockets
    - messageHandler.js          # Real-time message handling
    - notificationHandler.js     # Notification handling
```

### 3. AI Provider Integration

The AI Provider Integration layer connects to various AI services and manages their usage.

```
/ai-providers
  /openai
    - client.js                  # OpenAI API client
    - models.js                  # OpenAI model configurations
    - functions.js               # Function calling utilities
  /anthropic
    - client.js                  # Claude API client
    - models.js                  # Claude model configurations
  /google
    - client.js                  # Gemini API client
    - models.js                  # Gemini model configurations
  /deepseek
    - client.js                  # DeepSeek API client
    - models.js                  # DeepSeek model configurations
  /grok
    - client.js                  # Grok API client
    - models.js                  # Grok model configurations
  /common
    - modelSelector.js           # Model selection logic
    - fallbackHandler.js         # Provider fallback mechanisms
    - rateManager.js             # Rate limit management
```

### 4. Tool Integration

The Tool Integration layer provides access to external tools and services.

```
/tools
  /web
    - browserTool.js             # Web browsing capabilities
    - searchTool.js              # Search engine integration
  /data
    - databaseTool.js            # Database access
    - visualizationTool.js       # Data visualization
    - analysisTool.js            # Statistical analysis
  /code
    - executionTool.js           # Code execution environment
    - repositoryTool.js          # Version control integration
    - completionTool.js          # Code completion
  /document
    - pdfTool.js                 # PDF processing
    - officeTool.js              # Office document handling
    - markdownTool.js            # Markdown processing
  /common
    - toolRegistry.js            # Tool registration and discovery
    - permissionManager.js       # Tool access permissions
```

## Integration Strategy

### Phase 1: Backend Service Setup

1. **Core Service Implementation**
   - Implement the orchestration service for agent coordination
   - Create specialized agent services with placeholder functionality
   - Set up the conversation management system
   - Implement the context tracking mechanism

2. **Data Model Implementation**
   - Define conversation data structures
   - Create agent configuration models
   - Implement user profile models
   - Define tool interface models

3. **Utility Implementation**
   - Build the agent selection logic
   - Implement context management utilities
   - Create token counting services
   - Develop reusable prompt templates

### Phase 2: API Layer Implementation

1. **RESTful API Development**
   - Create conversation management endpoints
   - Implement agent configuration endpoints
   - Develop tool access endpoints
   - Build user management endpoints

2. **WebSocket Implementation**
   - Set up real-time message handling
   - Implement typing indicators
   - Create notification system
   - Develop connection management

3. **Middleware Development**
   - Implement authentication and authorization
   - Create rate limiting middleware
   - Develop error handling middleware
   - Build logging and monitoring middleware

### Phase 3: AI Provider Integration

1. **Provider Client Implementation**
   - Implement OpenAI client for GPT-4o
   - Create Claude client for Claude 3.5
   - Develop Gemini client for Gemini 1.5 Pro
   - Implement DeepSeek client
   - Create Grok client

2. **Model Management**
   - Implement model selection logic
   - Create fallback mechanisms
   - Develop cost optimization strategies
   - Build caching mechanisms

3. **Provider-Specific Optimizations**
   - Optimize prompts for each provider
   - Implement provider-specific error handling
   - Create specialized parsing for different response formats
   - Develop provider-specific rate limit handling

### Phase 4: Tool Integration

1. **Core Tool Implementation**
   - Implement web browsing capabilities
   - Create data analysis tools
   - Develop code execution environment
   - Build document processing tools

2. **Tool Management**
   - Create tool registry system
   - Implement permission management
   - Develop tool execution monitoring
   - Build tool result caching

3. **Specialized Tool Development**
   - Implement scientific research tools
   - Create academic citation tools
   - Develop data visualization tools
   - Build collaborative editing tools

## Integration with Frontend

### 1. API Client Integration

The frontend applications will connect to the backend through a unified API client:

```javascript
// /shared/api/synergosApiClient.js

import ApiClient from './apiClient';

class SynergosApiClient {
  constructor(config) {
    this.baseUrl = config.apiUrl;
    this.apiKey = config.apiKey;
    this.client = new ApiClient({
      baseUrl: this.baseUrl,
      apiKey: this.apiKey,
    });
    this.websocket = null;
  }

  // Conversation Management
  async getConversations(userId) {
    return this.client.request('/conversations', {
      method: 'GET',
      headers: {
        'User-ID': userId,
      },
    });
  }

  async createConversation(userId, title) {
    return this.client.request('/conversations', {
      method: 'POST',
      body: {
        userId,
        title,
        createdAt: new Date().toISOString(),
      },
    });
  }

  async sendMessage(conversationId, message) {
    return this.client.request(`/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: {
        content: message.content,
        sender: message.sender,
        timestamp: new Date().toISOString(),
        metadata: message.metadata || {},
      },
    });
  }

  // Agent Management
  async getAvailableAgents() {
    return this.client.request('/agents', {
      method: 'GET',
    });
  }

  async getAgentDetails(agentId) {
    return this.client.request(`/agents/${agentId}`, {
      method: 'GET',
    });
  }

  // Tool Access
  async executeTool(toolId, params) {
    return this.client.request(`/tools/${toolId}/execute`, {
      method: 'POST',
      body: {
        params,
      },
    });
  }

  async getAvailableTools() {
    return this.client.request('/tools', {
      method: 'GET',
    });
  }

  // WebSocket Connection
  connectWebSocket(userId, conversationId, handlers) {
    const wsUrl = `${this.baseUrl.replace('http', 'ws')}/ws?userId=${userId}&conversationId=${conversationId}`;
    
    this.websocket = new WebSocket(wsUrl);
    
    this.websocket.onopen = handlers.onOpen || (() => console.log('WebSocket connected'));
    this.websocket.onmessage = handlers.onMessage || ((event) => console.log('Message received:', event.data));
    this.websocket.onerror = handlers.onError || ((error) => console.error('WebSocket error:', error));
    this.websocket.onclose = handlers.onClose || (() => console.log('WebSocket closed'));
    
    return {
      send: (data) => this.websocket.send(JSON.stringify(data)),
      close: () => this.websocket.close(),
    };
  }
}

export default SynergosApiClient;
```

### 2. Redux Integration

The frontend state management will be connected to the backend services:

```javascript
// /shared/state/actions/conversationActions.js

import SynergosApiClient from '../../api/synergosApiClient';

const apiClient = new SynergosApiClient({
  apiUrl: process.env.API_URL,
  apiKey: process.env.API_KEY,
});

export const FETCH_CONVERSATIONS_REQUEST = 'FETCH_CONVERSATIONS_REQUEST';
export const FETCH_CONVERSATIONS_SUCCESS = 'FETCH_CONVERSATIONS_SUCCESS';
export const FETCH_CONVERSATIONS_FAILURE = 'FETCH_CONVERSATIONS_FAILURE';

export const CREATE_CONVERSATION_REQUEST = 'CREATE_CONVERSATION_REQUEST';
export const CREATE_CONVERSATION_SUCCESS = 'CREATE_CONVERSATION_SUCCESS';
export const CREATE_CONVERSATION_FAILURE = 'CREATE_CONVERSATION_FAILURE';

export const SEND_MESSAGE_REQUEST = 'SEND_MESSAGE_REQUEST';
export const SEND_MESSAGE_SUCCESS = 'SEND_MESSAGE_SUCCESS';
export const SEND_MESSAGE_FAILURE = 'SEND_MESSAGE_FAILURE';

export const RECEIVE_MESSAGE = 'RECEIVE_MESSAGE';

// Fetch conversations
export const fetchConversations = (userId) => async (dispatch) => {
  dispatch({ type: FETCH_CONVERSATIONS_REQUEST });
  
  try {
    const conversations = await apiClient.getConversations(userId);
    dispatch({
      type: FETCH_CONVERSATIONS_SUCCESS,
      payload: conversations,
    });
  } catch (error) {
    dispatch({
      type: FETCH_CONVERSATIONS_FAILURE,
      error: error.message,
    });
  }
};

// Create a new conversation
export const createConversation = (userId, title) => async (dispatch) => {
  dispatch({ type: CREATE_CONVERSATION_REQUEST });
  
  try {
    const conversation = await apiClient.createConversation(userId, title);
    dispatch({
      type: CREATE_CONVERSATION_SUCCESS,
      payload: conversation,
    });
    return conversation;
  } catch (error) {
    dispatch({
      type: CREATE_CONVERSATION_FAILURE,
      error: error.message,
    });
    throw error;
  }
};

// Send a message
export const sendMessage = (conversationId, message) => async (dispatch) => {
  dispatch({
    type: SEND_MESSAGE_REQUEST,
    payload: { conversationId, message },
  });
  
  try {
    const response = await apiClient.sendMessage(conversationId, message);
    dispatch({
      type: SEND_MESSAGE_SUCCESS,
      payload: { conversationId, message, response },
    });
    return response;
  } catch (error) {
    dispatch({
      type: SEND_MESSAGE_FAILURE,
      error: error.message,
      payload: { conversationId, message },
    });
    throw error;
  }
};

// Receive a message (typically from WebSocket)
export const receiveMessage = (conversationId, message) => ({
  type: RECEIVE_MESSAGE,
  payload: { conversationId, message },
});
```

### 3. WebSocket Integration

Real-time communication will be handled through WebSockets:

```javascript
// /shared/hooks/useWebSocket.js

import { useEffect, useRef, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { receiveMessage } from '../state/actions/conversationActions';
import SynergosApiClient from '../api/synergosApiClient';

export function useWebSocket(userId, conversationId) {
  const dispatch = useDispatch();
  const wsRef = useRef(null);
  const apiClient = useRef(new SynergosApiClient({
    apiUrl: process.env.API_URL,
    apiKey: process.env.API_KEY,
  })).current;

  useEffect(() => {
    if (!userId || !conversationId) return;

    const handlers = {
      onOpen: () => console.log('WebSocket connected'),
      onMessage: (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'message') {
            dispatch(receiveMessage(conversationId, data.message));
          } else if (data.type === 'typing') {
            // Handle typing indicator
          } else if (data.type === 'notification') {
            // Handle notification
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      },
      onError: (error) => console.error('WebSocket error:', error),
      onClose: () => console.log('WebSocket closed'),
    };

    wsRef.current = apiClient.connectWebSocket(userId, conversationId, handlers);

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [userId, conversationId, dispatch, apiClient]);

  const sendWebSocketMessage = useCallback((data) => {
    if (wsRef.current) {
      wsRef.current.send(data);
    }
  }, []);

  return {
    sendWebSocketMessage,
    isConnected: !!wsRef.current,
  };
}
```

## Backend Implementation Examples

### 1. Orchestration Service

```javascript
// /backend/services/orchestrationService.js

const AgentSelector = require('../utils/agentSelector');
const ContextManager = require('../utils/contextManager');
const TokenCounter = require('../utils/tokenCounter');
const PromptTemplates = require('../utils/promptTemplates');
const ModelSelector = require('../ai-providers/common/modelSelector');

class OrchestrationService {
  constructor(config) {
    this.agentSelector = new AgentSelector();
    this.contextManager = new ContextManager({
      tokenCounter: new TokenCounter(),
    });
    this.modelSelector = new ModelSelector(config.aiProviders);
    this.promptTemplates = new PromptTemplates();
    this.config = config;
  }

  async processMessage(conversationId, message, userId) {
    // Get conversation history
    const conversation = await this.getConversation(conversationId);
    
    // Update context with new message
    this.contextManager.addMessage({
      role: 'user',
      content: message.content,
    });
    
    // Determine the appropriate agent for this message
    const selectedAgent = this.agentSelector.selectAgent(message.content, conversation);
    
    // Select the appropriate AI model
    const model = this.modelSelector.selectModel(selectedAgent.provider, selectedAgent.modelPreference);
    
    // Generate the system prompt
    const systemPrompt = this.promptTemplates.getSystemPrompt(selectedAgent.type, {
      user: await this.getUserProfile(userId),
      conversation: conversation,
    });
    
    // Process the message with the selected agent
    const response = await this.callAgent(selectedAgent, {
      systemPrompt,
      messages: this.contextManager.getMessages(),
      model,
    });
    
    // Update context with response
    this.contextManager.addMessage({
      role: 'assistant',
      content: response.content,
      metadata: {
        agent: selectedAgent.type,
        model: model.name,
        provider: model.provider,
      },
    });
    
    // Save the updated conversation
    await this.saveConversation(conversationId, this.contextManager.getMessages());
    
    return {
      content: response.content,
      agent: selectedAgent.type,
      contextUtilization: this.contextManager.getContextUtilization(),
      metadata: response.metadata,
    };
  }

  async callAgent(agent, options) {
    // Call the appropriate agent service based on agent type
    switch (agent.type) {
      case 'research':
        const ResearchService = require('./researchService');
        const researchService = new ResearchService(this.config);
        return await researchService.processMessage(options);
      
      case 'content':
        const ContentService = require('./contentService');
        const contentService = new ContentService(this.config);
        return await contentService.processMessage(options);
      
      case 'data':
        const DataService = require('./dataService');
        const dataService = new DataService(this.config);
        return await dataService.processMessage(options);
      
      case 'code':
        const CodeService = require('./codeService');
        const codeService = new CodeService(this.config);
        return await codeService.processMessage(options);
      
      default:
        // Default to using the orchestration agent itself
        return await this.generateResponse(options);
    }
  }

  async generateResponse(options) {
    // Select the appropriate AI provider client
    const provider = this.modelSelector.getProviderClient(options.model.provider);
    
    // Generate the response
    const response = await provider.generateCompletion(
      options.messages,
      {
        model: options.model.name,
        systemPrompt: options.systemPrompt,
        temperature: 0.7,
        maxTokens: 2000,
      }
    );
    
    return {
      content: response.text,
      metadata: {
        usage: response.usage,
        model: response.model,
      },
    };
  }

  // Database interaction methods
  async getConversation(conversationId) {
    // Implementation depends on database choice
    // This is a placeholder
    return {
      id: conversationId,
      messages: [],
      // Other conversation data
    };
  }

  async saveConversation(conversationId, messages) {
    // Implementation depends on database choice
    // This is a placeholder
    console.log(`Saving conversation ${conversationId} with ${messages.length} messages`);
    return true;
  }

  async getUserProfile(userId) {
    // Implementation depends on database choice
    // This is a placeholder
    return {
      id: userId,
      preferences: {},
      // Other user data
    };
  }
}

module.exports = OrchestrationService;
```

### 2. Research Agent Service

```javascript
// /backend/services/researchService.js

const TokenCounter = require('../utils/tokenCounter');
const ToolRegistry = require('../tools/common/toolRegistry');

class ResearchService {
  constructor(config) {
    this.config = config;
    this.tokenCounter = new TokenCounter();
    this.toolRegistry = new ToolRegistry();
    
    // Register research-specific tools
    this.toolRegistry.registerTool('web_search', require('../tools/web/searchTool'));
    this.toolRegistry.registerTool('web_browse', require('../tools/web/browserTool'));
    this.toolRegistry.registerTool('pdf_reader', require('../tools/document/pdfTool'));
    this.toolRegistry.registerTool('database_query', require('../tools/data/databaseTool'));
  }

  async processMessage(options) {
    // Extract the research query from the messages
    const query = this.extractResearchQuery(options.messages);
    
    // Determine which tools to use
    const selectedTools = this.selectTools(query);
    
    // Execute research steps
    const researchResults = await this.executeResearch(query, selectedTools);
    
    // Generate a comprehensive response using Claude
    const response = await this.generateResponse(options, researchResults);
    
    return response;
  }

  extractResearchQuery(messages) {
    // Get the latest user message
    const userMessages = messages.filter(m => m.role === 'user');
    const latestUserMessage = userMessages[userMessages.length - 1];
    
    return latestUserMessage.content;
  }

  selectTools(query) {
    const selectedTools = [];
    
    // Simple keyword-based tool selection
    if (query.includes('search') || query.includes('find') || query.includes('information')) {
      selectedTools.push('web_search');
    }
    
    if (query.includes('website') || query.includes('webpage') || query.includes('article')) {
      selectedTools.push('web_browse');
    }
    
    if (query.includes('pdf') || query.includes('document') || query.includes('paper')) {
      selectedTools.push('pdf_reader');
    }
    
    if (query.includes('database') || query.includes('data') || query.includes('statistics')) {
      selectedTools.push('database_query');
    }
    
    // If no specific tools were selected, default to web search
    if (selectedTools.length === 0) {
      selectedTools.push('web_search');
    }
    
    return selectedTools;
  }

  async executeResearch(query, selectedTools) {
    const results = [];
    
    // Execute each selected tool
    for (const toolId of selectedTools) {
      const tool = this.toolRegistry.getTool(toolId);
      
      if (tool) {
        try {
          const result = await tool.execute({ query });
          results.push({
            tool: toolId,
            result,
          });
        } catch (error) {
          console.error(`Error executing tool ${toolId}:`, error);
          results.push({
            tool: toolId,
            error: error.message,
          });
        }
      }
    }
    
    return results;
  }

  async generateResponse(options, researchResults) {
    // Select the Claude provider for research responses
    const AnthropicClient = require('../ai-providers/anthropic/client');
    const anthropicClient = new AnthropicClient(this.config.aiProviders.anthropic);
    
    // Prepare the research summary
    const researchSummary = this.prepareResearchSummary(researchResults);
    
    // Add the research results to the system prompt
    const enhancedSystemPrompt = `${options.systemPrompt}\n\nResearch results:\n${researchSummary}`;
    
    // Generate the response
    const response = await anthropicClient.generateCompletion(
      options.messages,
      {
        model: 'claude-3-5-sonnet',
        systemPrompt: enhancedSystemPrompt,
        temperature: 0.3, // Lower temperature for more factual responses
        maxTokens: 2000,
      }
    );
    
    return {
      content: response.text,
      metadata: {
        usage: response.usage,
        model: response.model,
        researchTools: researchResults.map(r => r.tool),
      },
    };
  }

  prepareResearchSummary(researchResults) {
    let summary = '';
    
    for (const result of researchResults) {
      summary += `### ${result.tool.toUpperCase()} RESULTS:\n`;
      
      if (result.error) {
        summary += `Error: ${result.error}\n\n`;
      } else {
        // Format the result based on the tool type
        switch (result.tool) {
          case 'web_search':
            summary += this.formatSearchResults(result.result);
            break;
          case 'web_browse':
            summary += this.formatWebContent(result.result);
            break;
          case 'pdf_reader':
            summary += this.formatPdfContent(result.result);
            break;
          case 'database_query':
            summary += this.formatDatabaseResults(result.result);
            break;
          default:
            summary += JSON.stringify(result.result, null, 2);
        }
        
        summary += '\n\n';
      }
    }
    
    return summary;
  }

  formatSearchResults(results) {
    let formatted = '';
    
    if (Array.isArray(results)) {
      for (const item of results) {
        formatted += `- Title: ${item.title}\n`;
        formatted += `  URL: ${item.url}\n`;
        formatted += `  Snippet: ${item.snippet}\n\n`;
      }
    } else {
      formatted = JSON.stringify(results, null, 2);
    }
    
    return formatted;
  }

  formatWebContent(content) {
    // Extract the main content and format it
    return content.text || JSON.stringify(content, null, 2);
  }

  formatPdfContent(content) {
    // Format the extracted PDF text
    return content.text || JSON.stringify(content, null, 2);
  }

  formatDatabaseResults(results) {
    // Format database query results
    if (results.columns && results.rows) {
      let formatted = `Columns: ${results.columns.join(', ')}\n\nRows:\n`;
      
      for (const row of results.rows) {
        formatted += `- ${Object.values(row).join(', ')}\n`;
      }
      
      return formatted;
    }
    
    return JSON.stringify(results, null, 2);
  }
}

module.exports = ResearchService;
```

### 3. API Controller Example

```javascript
// /api/controllers/conversationController.js

const OrchestrationService = require('../../backend/services/orchestrationService');
const config = require('../../backend/config/serviceConfig');

const orchestrationService = new OrchestrationService(config);

// Get all conversations for a user
exports.getConversations = async (req, res) => {
  try {
    const userId = req.headers['user-id'];
    
    if (!userId) {
      return res.status(400).json({ error: 'User ID is required' });
    }
    
    // Implementation depends on database choice
    // This is a placeholder
    const conversations = []; // Get from database
    
    return res.status(200).json(conversations);
  } catch (error) {
    console.error('Error getting conversations:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

// Create a new conversation
exports.createConversation = async (req, res) => {
  try {
    const { userId, title } = req.body;
    
    if (!userId) {
      return res.status(400).json({ error: 'User ID is required' });
    }
    
    // Implementation depends on database choice
    // This is a placeholder
    const conversation = {
      id: `conv_${Date.now()}`,
      title: title || 'New Conversation',
      userId,
      createdAt: new Date().toISOString(),
      messages: [],
    };
    
    // Save to database
    
    return res.status(201).json(conversation);
  } catch (error) {
    console.error('Error creating conversation:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

// Send a message in a conversation
exports.sendMessage = async (req, res) => {
  try {
    const conversationId = req.params.conversationId;
    const { content, sender, metadata } = req.body;
    const userId = req.headers['user-id'];
    
    if (!conversationId || !content || !sender || !userId) {
      return res.status(400).json({ error: 'Conversation ID, content, sender, and user ID are required' });
    }
    
    // Create the message object
    const message = {
      id: `msg_${Date.now()}`,
      content,
      sender,
      timestamp: new Date().toISOString(),
      metadata: metadata || {},
    };
    
    // If the sender is the user, process with the orchestration service
    if (sender === 'user') {
      const response = await orchestrationService.processMessage(conversationId, message, userId);
      
      // Return both the user message and the AI response
      return res.status(200).json({
        userMessage: message,
        aiResponse: {
          id: `msg_${Date.now() + 1}`,
          content: response.content,
          sender: response.agent,
          timestamp: new Date().toISOString(),
          metadata: response.metadata,
        },
        contextUtilization: response.contextUtilization,
      });
    } else {
      // If the sender is not the user, just save the message
      // Implementation depends on database choice
      // This is a placeholder
      
      return res.status(200).json({ message });
    }
  } catch (error) {
    console.error('Error sending message:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

// Get messages for a conversation
exports.getMessages = async (req, res) => {
  try {
    const conversationId = req.params.conversationId;
    
    if (!conversationId) {
      return res.status(400).json({ error: 'Conversation ID is required' });
    }
    
    // Implementation depends on database choice
    // This is a placeholder
    const messages = []; // Get from database
    
    return res.status(200).json(messages);
  } catch (error) {
    console.error('Error getting messages:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};
```

### 4. WebSocket Handler

```javascript
// /api/websockets/messageHandler.js

const WebSocket = require('ws');
const OrchestrationService = require('../../backend/services/orchestrationService');
const config = require('../../backend/config/serviceConfig');

const orchestrationService = new OrchestrationService(config);

// Map of active connections
const connections = new Map();

// Initialize WebSocket server
exports.initialize = (server) => {
  const wss = new WebSocket.Server({ server });
  
  wss.on('connection', (ws, req) => {
    // Parse query parameters
    const url = new URL(req.url, 'http://localhost');
    const userId = url.searchParams.get('userId');
    const conversationId = url.searchParams.get('conversationId');
    
    if (!userId || !conversationId) {
      ws.close(1008, 'User ID and Conversation ID are required');
      return;
    }
    
    // Store the connection
    const connectionId = `${userId}:${conversationId}`;
    connections.set(connectionId, ws);
    
    console.log(`WebSocket connection established for ${connectionId}`);
    
    // Send a welcome message
    ws.send(JSON.stringify({
      type: 'connection',
      status: 'connected',
      timestamp: new Date().toISOString(),
    }));
    
    // Handle incoming messages
    ws.on('message', async (message) => {
      try {
        const data = JSON.parse(message);
        
        if (data.type === 'message') {
          // Handle user message
          const userMessage = {
            id: `msg_${Date.now()}`,
            content: data.content,
            sender: 'user',
            timestamp: new Date().toISOString(),
            metadata: data.metadata || {},
          };
          
          // Send typing indicator
          ws.send(JSON.stringify({
            type: 'typing',
            status: 'started',
            agent: 'system',
            timestamp: new Date().toISOString(),
          }));
          
          // Process the message
          const response = await orchestrationService.processMessage(
            conversationId,
            userMessage,
            userId
          );
          
          // Send typing indicator (stopped)
          ws.send(JSON.stringify({
            type: 'typing',
            status: 'stopped',
            agent: 'system',
            timestamp: new Date().toISOString(),
          }));
          
          // Send the AI response
          ws.send(JSON.stringify({
            type: 'message',
            message: {
              id: `msg_${Date.now()}`,
              content: response.content,
              sender: response.agent,
              timestamp: new Date().toISOString(),
              metadata: response.metadata,
            },
            contextUtilization: response.contextUtilization,
            timestamp: new Date().toISOString(),
          }));
        } else if (data.type === 'typing') {
          // Handle typing indicator
          ws.send(JSON.stringify({
            type: 'typing',
            status: data.status,
            timestamp: new Date().toISOString(),
          }));
        }
      } catch (error) {
        console.error('Error handling WebSocket message:', error);
        
        // Send error message
        ws.send(JSON.stringify({
          type: 'error',
          error: 'Error processing message',
          timestamp: new Date().toISOString(),
        }));
      }
    });
    
    // Handle connection close
    ws.on('close', () => {
      console.log(`WebSocket connection closed for ${connectionId}`);
      connections.delete(connectionId);
    });
    
    // Handle errors
    ws.on('error', (error) => {
      console.error(`WebSocket error for ${connectionId}:`, error);
    });
  });
  
  return wss;
};

// Send a message to a specific connection
exports.sendMessage = (userId, conversationId, message) => {
  const connectionId = `${userId}:${conversationId}`;
  const ws = connections.get(connectionId);
  
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message));
    return true;
  }
  
  return false;
};

// Broadcast a message to all connections
exports.broadcast = (message) => {
  connections.forEach((ws) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    }
  });
};
```

## Deployment Architecture

The backend integration will be deployed using a scalable architecture:

1. **API Gateway Layer**
   - Deployed as serverless functions (AWS Lambda, Google Cloud Functions)
   - Load balanced for high availability
   - API rate limiting and authentication

2. **Backend Services Layer**
   - Containerized microservices (Docker)
   - Orchestrated with Kubernetes
   - Auto-scaling based on demand

3. **Database Layer**
   - Document database for conversations (MongoDB)
   - Key-value store for caching (Redis)
   - Object storage for files (S3)

4. **AI Provider Integration**
   - Managed through a service mesh
   - Circuit breakers for reliability
   - Fallback mechanisms for provider outages

5. **WebSocket Layer**
   - Dedicated WebSocket servers
   - Connection pooling
   - Persistent connections with heartbeats

## Security Considerations

1. **Authentication and Authorization**
   - JWT-based authentication
   - Role-based access control
   - API key management

2. **Data Protection**
   - Encryption in transit (TLS)
   - Encryption at rest
   - PII handling according to regulations

3. **API Security**
   - Input validation
   - Rate limiting
   - CORS configuration

4. **AI Provider Security**
   - Secure API key storage
   - Request/response sanitization
   - Content filtering

## Monitoring and Logging

1. **Performance Monitoring**
   - API response times
   - Service health checks
   - Resource utilization

2. **Error Tracking**
   - Centralized error logging
   - Alert thresholds
   - Error categorization

3. **Usage Analytics**
   - Request volumes
   - AI provider usage
   - Cost tracking

4. **Audit Logging**
   - Security events
   - Administrative actions
   - Data access logs

## Next Steps

1. **Initial Backend Setup**
   - Implement core orchestration service
   - Create API gateway structure
   - Set up WebSocket server

2. **AI Provider Integration**
   - Implement provider clients
   - Create model selection logic
   - Set up fallback mechanisms

3. **Tool Integration**
   - Implement core tools
   - Create tool registry
   - Develop permission system

4. **Frontend Integration**
   - Connect API client to backend
   - Implement WebSocket handling
   - Create Redux integration

This backend integration plan provides a comprehensive approach to connecting the Synergos AI multi-agent system with the cross-platform frontend architecture. The implementation follows best practices for scalability, security, and maintainability, ensuring a robust foundation for the Synergos AI platform.
