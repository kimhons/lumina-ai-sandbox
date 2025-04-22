# Enterprise Integration Service Documentation

## Overview

The Enterprise Integration Service is a microservice component of the Lumina AI platform that enables seamless connectivity with various enterprise systems. It provides a unified interface for interacting with external enterprise systems such as Salesforce, Microsoft Teams, and SAP.

This service is designed to be:
- **Secure**: Implements robust authentication and encryption mechanisms
- **Scalable**: Built on a microservices architecture for horizontal scaling
- **Flexible**: Supports multiple enterprise systems through a pluggable adapter architecture
- **Observable**: Comprehensive monitoring and logging capabilities

## Architecture

The Enterprise Integration Service follows a layered architecture:

1. **API Layer**: REST controllers for system management and operation execution
2. **Service Layer**: Business logic for integration operations
3. **Adapter Layer**: System-specific implementations for different enterprise systems
4. **Security Layer**: Authentication, authorization, and credential management
5. **Data Layer**: Persistence of system configurations and operational data

## Key Components

### Enterprise System Management

The service provides CRUD operations for managing enterprise system configurations:

- **Register System**: Add a new enterprise system configuration
- **Update System**: Modify an existing system configuration
- **Get System**: Retrieve a system configuration by ID
- **List Systems**: List all system configurations with optional filtering
- **Delete System**: Remove a system configuration

### Integration Operations

The service supports executing operations on enterprise systems:

- **Execute Operation**: Perform an operation on a specific enterprise system
- **Execute Batch Operation**: Perform batch operations for improved performance
- **Register Webhook**: Set up webhooks for event-driven integration

### Security Management

The service includes security features for credential management:

- **Store Credentials**: Securely store authentication credentials
- **Rotate Credentials**: Update credentials for security purposes
- **Verify Webhook Signatures**: Validate incoming webhook requests

## Supported Enterprise Systems

### Salesforce

- **Operations**: SOQL queries, record creation/update/deletion, bulk operations
- **Authentication**: OAuth 2.0
- **Events**: Platform Events for webhooks

### Microsoft Teams

- **Operations**: Team/channel management, message sending
- **Authentication**: OAuth 2.0
- **Events**: Microsoft Graph subscriptions

### SAP

- **Operations**: OData queries, entity operations, function calls
- **Authentication**: Basic Auth, OAuth 2.0
- **Events**: OData change tracking

## API Reference

### System Management

#### Register System
```
POST /api/v1/integration/systems
```
Request body:
```json
{
  "systemId": "salesforce-prod",
  "systemType": "salesforce",
  "name": "Salesforce Production",
  "description": "Production Salesforce instance",
  "enabled": true,
  "connectionParams": {
    "instance_url": "https://mycompany.salesforce.com",
    "api_version": "v58.0"
  },
  "authParams": {
    "type": "oauth2"
  },
  "transformParams": {
    "rules": {}
  },
  "metadata": {
    "supports_webhooks": true
  }
}
```

#### Update System
```
PUT /api/v1/integration/systems/{systemId}
```

#### Get System
```
GET /api/v1/integration/systems/{systemId}
```

#### List Systems
```
GET /api/v1/integration/systems?systemType={type}&enabledOnly={true|false}
```

#### Delete System
```
DELETE /api/v1/integration/systems/{systemId}
```

### Integration Operations

#### Execute Operation
```
POST /api/v1/integration/execute
```
Request body:
```json
{
  "systemId": "salesforce-prod",
  "operation": "query",
  "params": {
    "soql": "SELECT Id, Name FROM Account LIMIT 10"
  },
  "context": {
    "requestId": "req-12345",
    "userId": "user-67890"
  }
}
```

#### Store Credentials
```
POST /api/v1/integration/systems/{systemId}/credentials
```
Request body:
```json
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "token_url": "https://login.salesforce.com/services/oauth2/token"
}
```

## Configuration

The service can be configured through the `application.yml` file or environment variables:

```yaml
integration:
  security:
    secret-key: ${INTEGRATION_SECRET_KEY:lumina-integration-secret-key}
    token-validity: 86400
  monitoring:
    metrics-enabled: true
    logging-enabled: true
  adapters:
    connection-timeout: 5000
    read-timeout: 10000
    max-connections: 100
```

## Deployment

The service is deployed as a Docker container and can be run using the provided Dockerfile:

```dockerfile
FROM openjdk:11-jre-slim
WORKDIR /app
COPY target/integration-service-0.0.1-SNAPSHOT.jar app.jar
EXPOSE 8085
ENTRYPOINT ["java", "-jar", "app.jar"]
```

It can be deployed as part of the Lumina AI microservices architecture using the docker-compose.yml file:

```yaml
integration-service:
  build:
    context: ./integration-service
    dockerfile: Dockerfile
  ports:
    - "8085:8085"
  environment:
    - SPRING_PROFILES_ACTIVE=dev
    - DISCOVERY_SERVICE_URL=http://discovery-service:8761/eureka/
    - INTEGRATION_SECRET_KEY=lumina-integration-secret-key
  depends_on:
    - discovery-service
    - postgres
  volumes:
    - ./integration-service:/app
  networks:
    - lumina-network
```

## Security Considerations

- All sensitive credentials are encrypted at rest
- JWT authentication is used for API access
- Webhook signatures are verified to prevent tampering
- TLS is used for all external communications

## Monitoring and Observability

The service exposes metrics and health information through Spring Boot Actuator:

- Health endpoint: `/actuator/health`
- Metrics endpoint: `/actuator/prometheus`
- Info endpoint: `/actuator/info`

## Error Handling

The service uses standard HTTP status codes for error responses:

- 400: Bad Request - Invalid input parameters
- 401: Unauthorized - Authentication failure
- 403: Forbidden - Authorization failure
- 404: Not Found - Resource not found
- 500: Internal Server Error - Unexpected error

Error responses include detailed information:

```json
{
  "requestId": "req-12345",
  "success": false,
  "errorMessage": "System not found: invalid-system",
  "errorCode": "INTEGRATION_ERROR",
  "executionTimeMs": 15
}
```

## Future Enhancements

Planned enhancements for future versions:

1. Support for additional enterprise systems (ServiceNow, Workday, etc.)
2. Enhanced caching for improved performance
3. Advanced transformation capabilities
4. Integration workflows for complex scenarios
5. Schema discovery for enterprise systems
