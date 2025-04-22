# Lumina AI Collaboration System Integration Documentation

## Overview

The Collaboration System is a core component of Lumina AI that enables multiple AI agents to work together effectively on complex tasks. This document provides comprehensive information on how to integrate the Collaboration System with other components of the Lumina AI platform.

## Architecture

The Collaboration System consists of the following key components:

1. **Team Formation Service**: Creates optimal teams of AI agents based on task requirements and agent capabilities
2. **Context Manager**: Ensures all team members share a consistent understanding of the task and environment
3. **Negotiation Protocol**: Facilitates structured negotiation for task allocation and conflict resolution
4. **Shared Memory System**: Provides unified memory access across team members
5. **Collaborative Learning**: Enables agents to learn from each other's experiences

## Integration Points

### 1. Integration with Provider System

The Collaboration System integrates with the Provider System to access AI agent capabilities and models:

```java
// Java example (collaboration-service)
@Service
public class ProviderIntegrationService {
    private final RestTemplate restTemplate;
    private final String providerServiceUrl;
    
    // Fetch agent capabilities from provider service
    public Map<String, Float> getAgentCapabilities(String agentId) {
        return restTemplate.getForObject(
            providerServiceUrl + "/api/v1/providers/agents/{agentId}/capabilities",
            Map.class,
            agentId
        );
    }
}
```

```python
# Python example (lumina-ai-monorepo)
class ProviderIntegration:
    def __init__(self, provider_client):
        self.provider_client = provider_client
        
    def get_agent_capabilities(self, agent_id):
        """Fetch agent capabilities from provider system"""
        return self.provider_client.get_agent_capabilities(agent_id)
```

### 2. Integration with Memory System

The Collaboration System integrates with the Memory System to access and store shared memories:

```java
// Java example (collaboration-service)
@Service
public class MemoryIntegrationService {
    private final RestTemplate restTemplate;
    private final String memoryServiceUrl;
    
    // Store shared memory in memory service
    public void storeSharedMemory(String key, Object value, String teamId) {
        MemoryRequest request = new MemoryRequest(key, value, teamId);
        restTemplate.postForEntity(
            memoryServiceUrl + "/api/v1/memory/store",
            request,
            Void.class
        );
    }
}
```

```python
# Python example (lumina-ai-monorepo)
class MemoryIntegration:
    def __init__(self, memory_client):
        self.memory_client = memory_client
        
    def store_shared_memory(self, key, value, team_id):
        """Store shared memory in memory system"""
        return self.memory_client.store(key, value, scope="team", scope_id=team_id)
```

### 3. Integration with Enterprise Systems

The Collaboration System integrates with the Enterprise Integration layer to access external enterprise systems:

```java
// Java example (collaboration-service)
@Service
public class EnterpriseIntegrationService {
    private final RestTemplate restTemplate;
    private final String integrationServiceUrl;
    
    // Access enterprise system data
    public Object getEnterpriseData(String system, String resource, Map<String, String> params) {
        return restTemplate.getForObject(
            integrationServiceUrl + "/api/v1/integration/{system}/{resource}",
            Object.class,
            system,
            resource,
            params
        );
    }
}
```

```python
# Python example (lumina-ai-monorepo)
class EnterpriseIntegration:
    def __init__(self, integration_gateway):
        self.integration_gateway = integration_gateway
        
    def get_enterprise_data(self, system, resource, params=None):
        """Access enterprise system data"""
        return self.integration_gateway.get_data(system, resource, params)
```

### 4. Integration with Orchestration System

The Collaboration System integrates with the Orchestration System to coordinate multi-agent workflows:

```java
// Java example (collaboration-service)
@Service
public class OrchestrationIntegrationService {
    private final RestTemplate restTemplate;
    private final String orchestrationServiceUrl;
    
    // Register team with orchestration system
    public void registerTeam(String teamId, List<String> agentIds, String taskId) {
        TeamRegistrationRequest request = new TeamRegistrationRequest(teamId, agentIds, taskId);
        restTemplate.postForEntity(
            orchestrationServiceUrl + "/api/v1/orchestration/teams",
            request,
            Void.class
        );
    }
}
```

```python
# Python example (lumina-ai-monorepo)
class OrchestrationIntegration:
    def __init__(self, orchestration_manager):
        self.orchestration_manager = orchestration_manager
        
    def register_team(self, team_id, agent_ids, task_id):
        """Register team with orchestration system"""
        return self.orchestration_manager.register_team(team_id, agent_ids, task_id)
```

## API Reference

### Collaboration Service REST API

#### Team Formation

- `POST /api/v1/collaboration/teams`: Form a team for a task
- `GET /api/v1/collaboration/teams/{teamId}`: Get a team by ID
- `GET /api/v1/collaboration/teams/by-task/{taskId}`: Get teams for a task
- `GET /api/v1/collaboration/teams/by-agent/{agentId}`: Get teams for an agent
- `PUT /api/v1/collaboration/teams/{teamId}/status`: Update team status
- `POST /api/v1/collaboration/teams/{teamId}/members`: Add a member to a team
- `DELETE /api/v1/collaboration/teams/{teamId}/members/{agentId}`: Remove a member from a team
- `DELETE /api/v1/collaboration/teams/{teamId}`: Disband a team

#### Context Management

- `POST /api/v1/collaboration/context`: Share context
- `GET /api/v1/collaboration/context/{contextId}`: Get a context item by ID
- `GET /api/v1/collaboration/context/by-key`: Get context items by key
- `GET /api/v1/collaboration/context/by-scope`: Get context items by scope and scope ID
- `GET /api/v1/collaboration/context/accessible-to/{agentId}`: Get context items accessible to an agent
- `PUT /api/v1/collaboration/context/{contextId}/value`: Update a context item's value
- `DELETE /api/v1/collaboration/context/{contextId}`: Delete a context item

#### Shared Memory

- `POST /api/v1/collaboration/memory`: Create a new memory item
- `GET /api/v1/collaboration/memory/{memoryId}`: Get a memory item by ID
- `GET /api/v1/collaboration/memory/by-key`: Get memory items by key
- `GET /api/v1/collaboration/memory/by-scope`: Get memory items by scope and scope ID
- `GET /api/v1/collaboration/memory/by-type`: Get memory items by memory type
- `GET /api/v1/collaboration/memory/by-tag`: Get memory items by tag
- `GET /api/v1/collaboration/memory/accessible-to/{agentId}`: Get memory items accessible to an agent
- `PUT /api/v1/collaboration/memory/{memoryId}/value`: Update a memory item's value
- `PUT /api/v1/collaboration/memory/{memoryId}/importance`: Update a memory item's importance
- `DELETE /api/v1/collaboration/memory/{memoryId}`: Delete a memory item

#### Negotiation

- `POST /api/v1/collaboration/negotiations`: Start a new negotiation
- `GET /api/v1/collaboration/negotiations/{negotiationId}`: Get a negotiation by ID
- `GET /api/v1/collaboration/negotiations/by-type`: Get negotiations by type
- `GET /api/v1/collaboration/negotiations/by-task/{taskId}`: Get negotiations for a task
- `GET /api/v1/collaboration/negotiations/by-team/{teamId}`: Get negotiations for a team
- `GET /api/v1/collaboration/negotiations/active`: Get active negotiations
- `POST /api/v1/collaboration/negotiations/{negotiationId}/counter-proposal`: Submit a counter-proposal
- `POST /api/v1/collaboration/negotiations/{negotiationId}/accept`: Accept the current proposal
- `POST /api/v1/collaboration/negotiations/{negotiationId}/reject`: Reject the current proposal
- `POST /api/v1/collaboration/negotiations/{negotiationId}/cancel`: Cancel a negotiation

#### Collaborative Learning

- `POST /api/v1/collaboration/learning`: Record a new learning event
- `GET /api/v1/collaboration/learning/{eventId}`: Get a learning event by ID
- `GET /api/v1/collaboration/learning/by-type`: Get learning events by type
- `GET /api/v1/collaboration/learning/by-agent/{agentId}`: Get learning events by agent
- `GET /api/v1/collaboration/learning/by-task/{taskId}`: Get learning events by task
- `GET /api/v1/collaboration/learning/by-team/{teamId}`: Get learning events by team
- `GET /api/v1/collaboration/learning/accessible-to/{agentId}`: Get learning events accessible to an agent
- `POST /api/v1/collaboration/learning/apply`: Apply learning from events to improve agent capabilities
- `POST /api/v1/collaboration/learning/share`: Share learning between team members

## Configuration

### Docker Compose Configuration

The Collaboration Service is configured in `docker-compose.yml`:

```yaml
collaboration-service:
  build:
    context: ./collaboration-service
    dockerfile: Dockerfile
  ports:
    - "8086:8085"
  environment:
    - SPRING_PROFILES_ACTIVE=dev
    - DISCOVERY_SERVICE_URL=http://discovery-service:8761/eureka/
    - SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/lumina_collaboration
    - SPRING_DATASOURCE_USERNAME=lumina
    - SPRING_DATASOURCE_PASSWORD=lumina_password
  depends_on:
    - discovery-service
    - postgres
    - integration-service
  volumes:
    - ./collaboration-service:/app
  networks:
    - lumina-network
```

### Kubernetes Configuration

The Collaboration Service is configured in Kubernetes manifests:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: collaboration-service
  namespace: lumina-ai
spec:
  replicas: 2
  selector:
    matchLabels:
      app: collaboration-service
  template:
    metadata:
      labels:
        app: collaboration-service
    spec:
      containers:
      - name: collaboration-service
        image: lumina-ai/collaboration-service:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8085
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "prod"
        - name: DISCOVERY_SERVICE_URL
          value: "http://discovery-service:8761/eureka/"
        - name: SPRING_DATASOURCE_URL
          value: "jdbc:postgresql://postgres:5432/lumina_collaboration"
        - name: SPRING_DATASOURCE_USERNAME
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: SPRING_DATASOURCE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
```

## Usage Examples

### Forming a Team for a Task

```java
// Java example
@RestController
public class TeamFormationExample {
    private final RestTemplate restTemplate;
    private final String collaborationServiceUrl;
    
    public void formTeamForTask(String taskId) {
        TeamFormationRequest request = new TeamFormationRequest();
        request.setTaskId(taskId);
        request.setStrategy("optimal");
        
        ResponseEntity<AgentTeam> response = restTemplate.postForEntity(
            collaborationServiceUrl + "/api/v1/collaboration/teams",
            request,
            AgentTeam.class
        );
        
        AgentTeam team = response.getBody();
        System.out.println("Team formed: " + team.getTeamId());
    }
}
```

```python
# Python example
def form_team_for_task(task_id):
    """Form a team for a task using the collaboration system"""
    collaboration_client = CollaborationClient()
    
    request = {
        "taskId": task_id,
        "strategy": "optimal"
    }
    
    team = collaboration_client.form_team(request)
    print(f"Team formed: {team['teamId']}")
    return team
```

### Sharing Context Between Agents

```java
// Java example
@Service
public class ContextSharingExample {
    private final RestTemplate restTemplate;
    private final String collaborationServiceUrl;
    
    public void shareContextWithTeam(String key, Object value, String teamId) {
        ContextSharingRequest request = new ContextSharingRequest();
        request.setKey(key);
        request.setValue(value);
        request.setContextType(ContextType.TASK_INFORMATION);
        request.setScope(ContextScope.TEAM);
        request.setScopeId(teamId);
        
        restTemplate.postForEntity(
            collaborationServiceUrl + "/api/v1/collaboration/context",
            request,
            ContextItem.class
        );
    }
}
```

```python
# Python example
def share_context_with_team(key, value, team_id):
    """Share context with a team using the collaboration system"""
    collaboration_client = CollaborationClient()
    
    request = {
        "key": key,
        "value": value,
        "contextType": "TASK_INFORMATION",
        "scope": "TEAM",
        "scopeId": team_id
    }
    
    context_item = collaboration_client.share_context(request)
    return context_item
```

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure the Collaboration Service is running and accessible
2. **Authentication Failed**: Verify that the correct credentials are provided
3. **Database Connection Failed**: Check the database connection parameters
4. **Service Discovery Failed**: Ensure the Discovery Service is running and accessible

### Logging

The Collaboration Service logs are available at:

- Docker: `docker logs <container_id>`
- Kubernetes: `kubectl logs -n lumina-ai deployment/collaboration-service`

## Security Considerations

1. **Authentication**: All API endpoints require authentication
2. **Authorization**: Access to team resources is restricted to team members
3. **Data Encryption**: Sensitive data is encrypted in transit and at rest
4. **Audit Logging**: All operations are logged for audit purposes

## Performance Considerations

1. **Caching**: Frequently accessed data is cached to improve performance
2. **Connection Pooling**: Database connections are pooled to reduce overhead
3. **Load Balancing**: Multiple instances of the service can be deployed for load balancing
4. **Rate Limiting**: API endpoints are rate-limited to prevent abuse

## Conclusion

The Collaboration System provides a robust foundation for multi-agent collaboration in Lumina AI. By following this integration guide, you can effectively leverage the collaboration capabilities in your applications and services.
