# Sample Code Examples for Building an Agentic System

This document provides practical code examples for implementing different aspects of an agentic system similar to Manus AI. These examples are designed to help users with some coding experience understand how to implement key components of an agentic system.

## 1. Basic Agent Setup with OpenAI

This example shows how to set up a simple agent using the OpenAI API:

```python
import os
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def simple_agent(user_query):
    """A simple agent that can respond to user queries."""
    
    # System instructions define the agent's behavior
    system_instructions = """
    You are a helpful assistant that can answer questions and perform tasks.
    When asked to perform a task, break it down into steps and explain your thinking.
    """
    
    # Create a conversation with the system instructions and user query
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_query}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    query = "I need to analyze the sentiment of customer reviews for my product."
    result = simple_agent(query)
    print(result)
```

## 2. Multi-Agent System with Handoffs

This example demonstrates how to create a system with multiple specialized agents and handoffs between them:

```python
import os
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class Agent:
    def __init__(self, name, instructions, model="gpt-3.5-turbo"):
        self.name = name
        self.instructions = instructions
        self.model = model
    
    def process(self, query, conversation_history=None):
        if conversation_history is None:
            conversation_history = []
        
        messages = [
            {"role": "system", "content": self.instructions}
        ] + conversation_history + [
            {"role": "user", "content": query}
        ]
        
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        
        return response.choices[0].message.content

class AgentSystem:
    def __init__(self, triage_agent, specialized_agents):
        self.triage_agent = triage_agent
        self.specialized_agents = specialized_agents
        self.conversation_history = []
    
    def process_query(self, query):
        # First, let the triage agent determine which specialized agent to use
        triage_instructions = f"""
        Determine which specialized agent should handle this query.
        Available agents: {', '.join([agent.name for agent in self.specialized_agents])}
        
        Respond ONLY with the name of the agent that should handle this query.
        """
        
        triage_result = self.triage_agent.process(
            triage_instructions + "\n\nQuery: " + query
        )
        
        # Find the appropriate specialized agent
        selected_agent = None
        for agent in self.specialized_agents:
            if agent.name.lower() in triage_result.lower():
                selected_agent = agent
                break
        
        # If no specialized agent was identified, use the triage agent
        if selected_agent is None:
            selected_agent = self.triage_agent
        
        # Process the query with the selected agent
        result = selected_agent.process(query, self.conversation_history)
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": query})
        self.conversation_history.append({"role": "assistant", "content": result})
        
        return {
            "agent": selected_agent.name,
            "response": result
        }

# Create specialized agents
research_agent = Agent(
    name="Research Agent",
    instructions="You are a research specialist. Your role is to find information, analyze data, and provide comprehensive answers to research questions.",
    model="gpt-4o"
)

coding_agent = Agent(
    name="Coding Agent",
    instructions="You are a coding specialist. Your role is to write, debug, and explain code. Provide clear, efficient, and well-commented code examples.",
    model="gpt-4o"
)

writing_agent = Agent(
    name="Writing Agent",
    instructions="You are a writing specialist. Your role is to create, edit, and improve written content. Focus on clarity, engagement, and proper structure.",
    model="gpt-4o"
)

# Create triage agent
triage_agent = Agent(
    name="Triage Agent",
    instructions="You are a triage agent. Your role is to understand user queries and direct them to the appropriate specialized agent.",
    model="gpt-3.5-turbo"
)

# Create the agent system
agent_system = AgentSystem(
    triage_agent=triage_agent,
    specialized_agents=[research_agent, coding_agent, writing_agent]
)

# Example usage
if __name__ == "__main__":
    queries = [
        "What are the latest developments in quantum computing?",
        "Write a Python function to calculate the Fibonacci sequence.",
        "Create a compelling product description for a new smartphone."
    ]
    
    for query in queries:
        result = agent_system.process_query(query)
        print(f"Query: {query}")
        print(f"Handled by: {result['agent']}")
        print(f"Response: {result['response'][:100]}...")  # Show first 100 chars
        print("-" * 50)
```

## 3. Tool-Using Agent with Web Browsing Capability

This example shows how to create an agent that can use tools, specifically a web browsing tool:

```python
import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class WebBrowserTool:
    def __init__(self):
        self.name = "web_browser"
        self.description = "A tool to search the web and retrieve information from websites."
    
    def search(self, query):
        """Simulate a web search (in a real implementation, use a search API)."""
        # This is a simplified example - in a real implementation, use a search API
        return f"Search results for: {query}\n1. Example.com: Information about {query}\n2. Wikipedia: {query} article"
    
    def get_webpage_content(self, url):
        """Get the content of a webpage."""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text content (simplified)
            text = soup.get_text()
            
            # Truncate to avoid token limits
            if len(text) > 2000:
                text = text[:2000] + "... (content truncated)"
            
            return text
        except Exception as e:
            return f"Error retrieving webpage: {str(e)}"

class ToolUsingAgent:
    def __init__(self):
        self.tools = {
            "web_browser": WebBrowserTool()
        }
    
    def process_query(self, query):
        # System instructions that describe available tools
        system_instructions = """
        You are a helpful assistant that can use tools to find information.
        
        Available tools:
        - web_browser: A tool to search the web and retrieve information from websites.
          - search(query): Search the web for information
          - get_webpage_content(url): Get the content of a specific webpage
        
        When you need to use a tool, respond with:
        ACTION: tool_name.function_name(parameters)
        
        After receiving the tool's output, provide your final answer.
        """
        
        # Start conversation with the user query
        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": query}
        ]
        
        # Maximum number of tool use iterations to prevent infinite loops
        max_iterations = 5
        iterations = 0
        
        while iterations < max_iterations:
            # Get the next action from the model
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_message})
            
            # Check if the response contains a tool action
            if "ACTION:" in assistant_message:
                # Extract the tool action
                action_line = [line for line in assistant_message.split('\n') if "ACTION:" in line][0]
                action = action_line.split("ACTION:")[1].strip()
                
                # Parse the tool, function, and parameters
                tool_function = action.split('(')[0].strip()
                tool_name, function_name = tool_function.split('.')
                
                # Extract parameters (simple parsing, could be improved)
                params_str = action.split('(')[1].split(')')[0]
                params = [p.strip().strip('"\'') for p in params_str.split(',')]
                
                # Execute the tool function
                tool_result = "Error: Tool or function not found."
                if tool_name in self.tools:
                    tool = self.tools[tool_name]
                    if function_name == "search" and len(params) > 0:
                        tool_result = tool.search(params[0])
                    elif function_name == "get_webpage_content" and len(params) > 0:
                        tool_result = tool.get_webpage_content(params[0])
                
                # Add the tool result to the conversation
                messages.append({"role": "user", "content": f"Tool result: {tool_result}\n\nPlease continue based on this information."})
                iterations += 1
            else:
                # If no tool action is requested, we have the final answer
                return assistant_message
        
        # If we've reached the maximum number of iterations, return the last response
        return messages[-1]["content"]

# Example usage
if __name__ == "__main__":
    agent = ToolUsingAgent()
    query = "What are the latest developments in renewable energy technology?"
    result = agent.process_query(query)
    print(f"Query: {query}")
    print(f"Response: {result}")
```

## 4. Multi-API Integration with Different LLM Providers

This example demonstrates how to create a system that can use different LLM providers (OpenAI, Anthropic, Google):

```python
import os
import requests
import json

class LLMProvider:
    """Base class for LLM providers."""
    def __init__(self, api_key):
        self.api_key = api_key
    
    def generate_text(self, prompt, system_instruction=None, temperature=0.7):
        """Generate text based on the prompt."""
        raise NotImplementedError("Subclasses must implement this method")

class OpenAIProvider(LLMProvider):
    """Provider for OpenAI models."""
    def __init__(self, api_key, model="gpt-3.5-turbo"):
        super().__init__(api_key)
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def generate_text(self, prompt, system_instruction=None, temperature=0.7):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code}, {response.text}"

class AnthropicProvider(LLMProvider):
    """Provider for Anthropic Claude models."""
    def __init__(self, api_key, model="claude-3-sonnet-20240229"):
        super().__init__(api_key)
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/messages"
    
    def generate_text(self, prompt, system_instruction=None, temperature=0.7):
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        
        if system_instruction:
            data["system"] = system_instruction
        
        response = requests.post(self.api_url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            return f"Error: {response.status_code}, {response.text}"

class GoogleProvider(LLMProvider):
    """Provider for Google Gemini models."""
    def __init__(self, api_key, model="gemini-pro"):
        super().__init__(api_key)
        self.model = model
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    def generate_text(self, prompt, system_instruction=None, temperature=0.7):
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature
            }
        }
        
        if system_instruction:
            data["contents"].insert(0, {
                "role": "system",
                "parts": [{"text": system_instruction}]
            })
        
        url = f"{self.api_url}?key={self.api_key}"
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error: {response.status_code}, {response.text}"

class MultiProviderAgent:
    """An agent that can use multiple LLM providers."""
    def __init__(self):
        # Initialize providers (in a real application, handle API keys securely)
        self.providers = {
            "openai": OpenAIProvider(api_key=os.environ.get("OPENAI_API_KEY", ""), model="gpt-4o"),
            "anthropic": AnthropicProvider(api_key=os.environ.get("ANTHROPIC_API_KEY", "")),
            "google": GoogleProvider(api_key=os.environ.get("GOOGLE_API_KEY", ""))
        }
        
        # Define provider specialties
        self.specialties = {
            "openai": ["coding", "technical", "data analysis"],
            "anthropic": ["writing", "creative", "ethical reasoning"],
            "google": ["research", "factual information", "summarization"]
        }
    
    def select_provider(self, query):
        """Select the most appropriate provider based on the query."""
        # Use OpenAI to classify the query (in a real implementation, this could be more sophisticated)
        classification_prompt = f"""
        Classify the following query into exactly one of these categories:
        - coding: Questions about programming, debugging, or technical implementation
        - technical: Technical questions about computers, software, or technology
        - data analysis: Questions about analyzing or visualizing data
        - writing: Requests for writing, editing, or creative content
        - creative: Requests for creative ideas, stories, or content
        - ethical reasoning: Questions about ethics, morality, or sensitive topics
        - research: Questions requiring factual research or information gathering
        - factual information: Questions about facts, definitions, or general knowledge
        - summarization: Requests to summarize or condense information
        
        Query: {query}
        
        Respond with only the category name, nothing else.
        """
        
        # Use OpenAI for classification (assuming it's available)
        if "openai" in self.providers:
            category = self.providers["openai"].generate_text(classification_prompt).strip().lower()
        else:
            # Fallback to a simple keyword-based approach
            category = "factual information"  # Default
            
            coding_keywords = ["code", "program", "function", "bug", "debug", "algorithm"]
            writing_keywords = ["write", "essay", "article", "story", "creative", "content"]
            research_keywords = ["research", "information", "find", "search", "data"]
            
            for word in coding_keywords:
                if word in query.lower():
                    category = "coding"
                    break
            
            for word in writing_keywords:
                if word in query.lower():
                    category = "writing"
                    break
            
            for word in research_keywords:
                if word in query.lower():
                    category = "research"
                    break
        
        # Select provider based on category
        for provider, categories in self.specialties.items():
            if category in categories and provider in self.providers:
                return provider
        
        # Default to OpenAI if available, otherwise use the first available provider
        return "openai" if "openai" in self.providers else list(self.providers.keys())[0]
    
    def process_query(self, query, system_instruction=None):
        """Process a query using the most appropriate provider."""
        provider_name = self.select_provider(query)
        provider = self.providers[provider_name]
        
        result = provider.generate_text(query, system_instruction)
        
        return {
            "provider": provider_name,
            "response": result
        }

# Example usage
if __name__ == "__main__":
    agent = MultiProviderAgent()
    
    queries = [
        "Write a Python function to find prime numbers.",
        "Write a creative short story about a robot learning to paint.",
        "What are the main causes of climate change?"
    ]
    
    for query in queries:
        result = agent.process_query(query)
        print(f"Query: {query}")
        print(f"Provider: {result['provider']}")
        print(f"Response: {result['response'][:100]}...")  # Show first 100 chars
        print("-" * 50)
```

## 5. No-Code Implementation with Langflow (Python Client)

This example shows how to interact with Langflow using its Python client:

```python
import requests
import json
import os

class LangflowClient:
    """A client for interacting with Langflow."""
    
    def __init__(self, base_url="https://cloud.langflow.org"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, password):
        """Log in to Langflow."""
        url = f"{self.base_url}/api/v1/login"
        data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return True
        else:
            print(f"Login failed: {response.status_code}, {response.text}")
            return False
    
    def get_flows(self):
        """Get all flows."""
        if not self.token:
            print("Not logged in")
            return None
        
        url = f"{self.base_url}/api/v1/flows"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get flows: {response.status_code}, {response.text}")
            return None
    
    def get_flow(self, flow_id):
        """Get a specific flow."""
        if not self.token:
            print("Not logged in")
            return None
        
        url = f"{self.base_url}/api/v1/flows/{flow_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get flow: {response.status_code}, {response.text}")
            return None
    
    def run_flow(self, flow_id, inputs):
        """Run a flow with the given inputs."""
        if not self.token:
            print("Not logged in")
            return None
        
        url = f"{self.base_url}/api/v1/flows/{flow_id}/run"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"inputs": inputs}
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to run flow: {response.status_code}, {response.text}")
            return None

# Example usage
if __name__ == "__main__":
    # Replace with your Langflow credentials
    username = os.environ.get("LANGFLOW_USERNAME")
    password = os.environ.get("LANGFLOW_PASSWORD")
    
    client = LangflowClient()
    
    if client.login(username, password):
        print("Login successful")
        
        # Get all flows
        flows = client.get_flows()
        if flows:
            print(f"Found {len(flows)} flows")
            
            # Use the first flow as an example
            if len(flows) > 0:
                flow_id = flows[0]["id"]
                print(f"Using flow: {flows[0]['name']} ({flow_id})")
                
                # Run the flow with a sample input
                result = client.run_flow(flow_id, {"input": "What is artificial intelligence?"})
                if result:
                    print("Flow result:")
                    print(result)
    else:
        print("Login failed")
```

## 6. Memory System for Agents

This example demonstrates how to implement a memory system for agents:

```python
import os
from openai import OpenAI
import json
from datetime import datetime
import sqlite3

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class MemorySystem:
    """A memory system for AI agents."""
    
    def __init__(self, db_path=":memory:"):
        """Initialize the memory system with a SQLite database."""
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Create the necessary tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Create a table for short-term memory (recent conversations)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS short_term_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            role TEXT,
            content TEXT
        )
        ''')
        
        # Create a table for long-term memory (important facts and information)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS long_term_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            category TEXT,
            fact TEXT,
            importance REAL
        )
        ''')
        
        self.conn.commit()
    
    def add_to_short_term_memory(self, role, content):
        """Add a message to short-term memory."""
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO short_term_memory (timestamp, role, content) VALUES (?, ?, ?)",
            (timestamp, role, content)
        )
        
        self.conn.commit()
    
    def get_short_term_memory(self, limit=10):
        """Get the most recent messages from short-term memory."""
        cursor = self.conn.cursor()
        
        cursor.execute(
            "SELECT timestamp, role, content FROM short_term_memory ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        
        # Reverse the results to get chronological order
        return list(reversed(cursor.fetchall()))
    
    def add_to_long_term_memory(self, category, fact, importance=0.5):
        """Add a fact to long-term memory."""
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO long_term_memory (timestamp, category, fact, importance) VALUES (?, ?, ?, ?)",
            (timestamp, category, fact, importance)
        )
        
        self.conn.commit()
    
    def get_relevant_long_term_memory(self, query, limit=5):
        """Get relevant facts from long-term memory based on the query."""
        # In a real implementation, use embeddings and vector search
        # For this example, we'll use a simple keyword search
        cursor = self.conn.cursor()
        
        # Split the query into keywords
        keywords = query.lower().split()
        
        # Prepare a list to store matching facts
        matching_facts = []
        
        # Get all facts from long-term memory
        cursor.execute("SELECT category, fact, importance FROM long_term_memory")
        facts = cursor.fetchall()
        
        # Score each fact based on keyword matches
        for category, fact, importance in facts:
            score = 0
            fact_lower = fact.lower()
            
            for keyword in keywords:
                if keyword in fact_lower or keyword in category.lower():
                    score += 1
            
            # Adjust score by importance
            score *= importance
            
            if score > 0:
                matching_facts.append((category, fact, score))
        
        # Sort by score and return the top results
        matching_facts.sort(key=lambda x: x[2], reverse=True)
        return matching_facts[:limit]
    
    def extract_facts(self, text):
        """Extract important facts from text to store in long-term memory."""
        # Use OpenAI to extract facts
        prompt = f"""
        Extract important facts from the following text. For each fact, provide:
        1. A category (e.g., "personal information", "preferences", "technical knowledge")
        2. The fact itself
        3. An importance score from 0.0 to 1.0
        
        Format your response as a JSON array of objects with "category", "fact", and "importance" fields.
        
        Text: {text}
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        try:
            facts_text = response.choices[0].message.content
            # Extract JSON from the response (it might be surrounded by markdown code blocks)
            if "```json" in facts_text:
                facts_text = facts_text.split("```json")[1].split("```")[0].strip()
            elif "```" in facts_text:
                facts_text = facts_text.split("```")[1].split("```")[0].strip()
            
            facts = json.loads(facts_text)
            return facts
        except Exception as e:
            print(f"Error extracting facts: {str(e)}")
            return []

class AgentWithMemory:
    """An agent with short-term and long-term memory."""
    
    def __init__(self, name, instructions):
        self.name = name
        self.instructions = instructions
        self.memory = MemorySystem()
    
    def process_query(self, query):
        # Get relevant context from memory
        short_term_context = self.memory.get_short_term_memory()
        long_term_context = self.memory.get_relevant_long_term_memory(query)
        
        # Format the context for the prompt
        context = "Previous conversation:\n"
        for _, role, content in short_term_context:
            context += f"{role.capitalize()}: {content}\n"
        
        context += "\nRelevant information from memory:\n"
        for category, fact, _ in long_term_context:
            context += f"- {category}: {fact}\n"
        
        # Create the full prompt
        full_prompt = f"{context}\n\nUser query: {query}"
        
        # Add the query to short-term memory
        self.memory.add_to_short_term_memory("user", query)
        
        # Generate a response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.instructions},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        
        # Add the response to short-term memory
        self.memory.add_to_short_term_memory("assistant", response_text)
        
        # Extract and store facts from the user query
        facts = self.memory.extract_facts(query)
        for fact in facts:
            self.memory.add_to_long_term_memory(
                fact["category"],
                fact["fact"],
                fact["importance"]
            )
        
        return response_text

# Example usage
if __name__ == "__main__":
    agent = AgentWithMemory(
        name="Personal Assistant",
        instructions="You are a helpful personal assistant. Use the provided context to personalize your responses."
    )
    
    # Simulate a conversation
    queries = [
        "My name is Alex and I work as a software engineer.",
        "I'm planning a trip to Japan next month.",
        "Can you recommend some good programming books?",
        "What should I pack for my Japan trip?"
    ]
    
    for query in queries:
        print(f"User: {query}")
        response = agent.process_query(query)
        print(f"Assistant: {response}")
        print("-" * 50)
```

## 7. Simple No-Code Implementation with Python Requests

This example shows how to interact with a no-code AI agent platform using Python requests:

```python
import requests
import os
import json

class NoCodeAgentClient:
    """A client for interacting with a no-code AI agent platform."""
    
    def __init__(self, platform="trilex"):
        self.platform = platform
        
        # Set the appropriate API URL based on the platform
        if platform == "trilex":
            self.api_url = "https://api.trilex.ai/v1"
            self.api_key = os.environ.get("TRILEX_API_KEY")
        elif platform == "bizway":
            self.api_url = "https://api.bizway.io/v1"
            self.api_key = os.environ.get("BIZWAY_API_KEY")
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def create_agent(self, name, description, capabilities=None):
        """Create a new agent on the platform."""
        if not capabilities:
            capabilities = ["text_generation", "web_search"]
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "name": name,
            "description": description,
            "capabilities": capabilities
        }
        
        response = requests.post(f"{self.api_url}/agents", headers=headers, json=data)
        
        if response.status_code in (200, 201):
            return response.json()
        else:
            print(f"Failed to create agent: {response.status_code}, {response.text}")
            return None
    
    def get_agents(self):
        """Get all agents."""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.get(f"{self.api_url}/agents", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get agents: {response.status_code}, {response.text}")
            return None
    
    def run_agent(self, agent_id, query, context=None):
        """Run an agent with the given query."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "query": query
        }
        
        if context:
            data["context"] = context
        
        response = requests.post(f"{self.api_url}/agents/{agent_id}/run", headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to run agent: {response.status_code}, {response.text}")
            return None

# Example usage (note: this is a simulated example as these APIs are hypothetical)
if __name__ == "__main__":
    # This is a simulated example - in a real implementation, use actual API endpoints
    client = NoCodeAgentClient(platform="trilex")
    
    # Create a new agent
    agent = client.create_agent(
        name="Research Assistant",
        description="An agent that helps with research tasks",
        capabilities=["text_generation", "web_search", "document_analysis"]
    )
    
    if agent:
        print(f"Created agent: {agent['name']} (ID: {agent['id']})")
        
        # Run the agent
        result = client.run_agent(
            agent_id=agent["id"],
            query="What are the latest advancements in renewable energy?",
            context={"preferred_sources": ["academic", "news"]}
        )
        
        if result:
            print("Agent response:")
            print(result["response"])
    else:
        print("Failed to create agent")
```

## Conclusion

These code examples provide a starting point for implementing different aspects of an agentic system similar to Manus AI. They cover basic agent setup, multi-agent systems, tool integration, multi-API integration, memory systems, and interaction with no-code platforms.

Remember that these examples are simplified for educational purposes. In a production environment, you would need to add error handling, security measures, and more robust implementations of each component.

For users with limited coding experience, the no-code and low-code platforms mentioned in the main guide (Langflow, Flowise, Trilex AI, etc.) offer more accessible ways to build agentic systems without writing extensive code.
