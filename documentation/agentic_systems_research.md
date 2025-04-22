# Research on Building an Agentic System Similar to Manus AI

## Introduction
This document compiles research findings on building an agentic system similar to Manus AI. The goal is to create a comprehensive guide for building a no-code/low-code agentic system that can perform tasks like information gathering, coding, web browsing, app building, technical research, and graphic design.

## OpenAI Cookbook - Agent Implementation Approaches

### How to build an agent with the OpenAI Node.js SDK
The OpenAI Cookbook provides a detailed guide on building an agent using the OpenAI Node.js SDK. Key components include:

1. **Function Calling**: Enables the app to take actions based on user inputs (search the web, send emails, book tickets)
2. **Tools Definition**: Creating a schema to describe functions for the AI to use
   ```javascript
   const tools = [
     {
       type: "function",
       function: {
         name: "functionName",
         description: "Description of what the function does",
         parameters: {
           type: "object",
           properties: {
             // Parameters the function accepts
           },
           required: ["param1", "param2"]
         }
       }
     }
   ]
   ```
3. **Messages Array**: Tracks conversation history between the user and AI
   ```javascript
   const messages = [
     {
       role: "system",
       content: "You are a helpful assistant. Only use the functions you have been provided with."
     }
   ]
   ```
4. **Agent Function**: The core logic that processes user input and decides which functions to call
   ```javascript
   async function agent(userInput) {
     messages.push({
       role: "user",
       content: userInput
     });
     const response = await openai.chat.completions.create({
       model: "gpt-4",
       messages: messages,
       tools: tools
     });
     // Process response and call appropriate functions
   }
   ```

This implementation demonstrates how OpenAI doesn't execute code directly but rather tells your application which functions to use in a given scenario.

## Google Cloud - Building an AI Agent with Gemini 1.5 Pro

The Google Cloud article provides insights on building an AI agent for trip planning using Gemini 1.5 Pro. Key concepts include:

1. **Function Calling**: Allows connecting Gemini models with external systems, APIs, and data sources to retrieve real-time information and perform actions.

2. **Grounding**: Enhances the model's ability to access and process information from external sources like documents, knowledge bases, and the web.

3. **Implementation Steps**:
   - Define potential user queries
   - Set up development environment
   - Configure API keys
   - Define custom functions for function calling
   - Declare custom functions as tools
   - Configure safety settings
   - Build the agent by mapping tool names to functions
   - Implement prompt engineering for better handling of user inputs

This approach demonstrates how to create an AI agent that can understand user requests, retrieve relevant information from external APIs, and provide personalized recommendations.

## Snowflake Guide - A Practical Guide to AI Agents

The Snowflake guide "A Practical Guide to AI Agents" provides valuable insights on agentic AI concepts, use cases, and implementation considerations. Key points include:

1. **Definition**: Agentic AI is designed to function autonomously, making decisions, performing tasks, and adapting to its environment without constant human intervention.

2. **Differences**: The guide explains how agentic AI differs from traditional AI and generative AI.

3. **Key Benefits**: Outlines the benefits of agentic technology across business functions and industries.

4. **Implementation Considerations**: Covers security, compliance, and ethical AI deployment.

5. **Roadmap**: Provides five considerations for implementing agentic AI in organizations.

## Key Components for Building an Agentic System

Based on the research so far, these are the essential components needed to build an agentic system similar to Manus AI:

1. **Large Language Model Integration**: Using models like GPT-4, Gemini 1.5 Pro, Claude, or Grok as the core reasoning engine.

2. **Function Calling Framework**: A system that allows the AI to determine which functions to call based on user input.

3. **Tools and APIs Integration**: Connecting to external tools and APIs for real-time data and actions.

4. **Memory and Context Management**: Tracking conversation history and maintaining context.

5. **Guardrails and Safety Measures**: Implementing safety settings to prevent harmful outputs.

6. **User Interface**: Creating a user-friendly interface for interaction with the agent.

7. **Feedback Mechanisms**: Systems to learn from user feedback and improve over time.

## Next Steps

Further research is needed on:
1. Additional agentic systems and frameworks
2. Detailed analysis of Manus AI capabilities
3. No-code/low-code approaches for beginners
4. Multi-API integration strategies
5. Implementation approaches for specific capabilities (web browsing, coding, etc.)
