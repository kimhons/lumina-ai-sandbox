# Enhanced Learning Service

This service implements the Enhanced Learning System for Lumina AI, providing sophisticated learning capabilities, continuous learning from user interactions, explainable AI, knowledge transfer between agents, and integration with the Multi-Agent Collaboration System.

## Key Features

### Core Learning Capabilities
- **Model Registry**: Centralized management of learning models
- **Feature Engineering Pipeline**: Advanced data transformation for learning
- **Learning Algorithm Factory**: Flexible algorithm selection and configuration
- **Evaluation Framework**: Comprehensive model performance assessment

### Advanced Learning Features
- **Continuous Learning**: Real-time adaptation from user interactions
- **Explainable AI**: Transparent decision-making with multiple explanation methods
- **Knowledge Transfer**: Efficient sharing of knowledge between agents
- **Privacy-Preserving Learning**: Protection of user data during learning

### Integration Features
- **Knowledge Transfer Integration**: Share knowledge between agents with appropriate permissions
- **Collaborative Learning**: Team-based learning with federated learning capabilities
- **Problem Solving**: Collaborative approach to complex problems through decomposition and coordination

## API Endpoints

### Knowledge Transfer
- `POST /api/v1/knowledge/transfer`: Transfer knowledge between agents
- `POST /api/v1/knowledge/broadcast`: Broadcast knowledge to a team
- `POST /api/v1/knowledge/query/{agentId}`: Query an agent's knowledge
- `POST /api/v1/knowledge`: Create a new knowledge item

### Collaborative Learning
- `POST /api/v1/learning/collaborative/teams/form`: Form a learning team
- `POST /api/v1/learning/collaborative/contexts`: Create a learning context
- `POST /api/v1/learning/collaborative/tasks/distribute`: Distribute learning tasks
- `POST /api/v1/learning/collaborative/federated`: Coordinate federated learning
- `POST /api/v1/learning/collaborative/complete/{contextId}`: Complete a learning session
- `GET /api/v1/learning/collaborative/sessions/{sessionId}`: Get a learning session
- `GET /api/v1/learning/collaborative/sessions`: Get all learning sessions
- `GET /api/v1/learning/collaborative/sessions/team/{teamId}`: Get sessions by team

### Problem Solving
- `POST /api/v1/problem-solving/analyze`: Analyze a problem
- `POST /api/v1/problem-solving/decompose`: Decompose a problem
- `POST /api/v1/problem-solving/teams/form`: Form a problem-solving team
- `POST /api/v1/problem-solving/contexts`: Create a problem-solving context
- `POST /api/v1/problem-solving/coordinate`: Coordinate problem solving
- `POST /api/v1/problem-solving/solve`: Solve a problem
- `GET /api/v1/problem-solving/sessions/{sessionId}`: Get a problem-solving session
- `GET /api/v1/problem-solving/sessions`: Get all problem-solving sessions
- `GET /api/v1/problem-solving/sessions/team/{teamId}`: Get sessions by team
- `GET /api/v1/problem-solving/sessions/type/{problemType}`: Get sessions by problem type

## Integration with Other Services

This service integrates with:
- **Collaboration Service**: For team formation, context management, and task distribution
- **Integration Service**: For connecting with enterprise systems
- **UI Service**: For providing learning capabilities to the user interface

## Security and Privacy

The service implements several security and privacy measures:
- **Permission-based knowledge sharing**: Knowledge is shared only with appropriate permissions
- **Differential privacy**: Learning algorithms implement differential privacy to protect sensitive data
- **Federated learning**: Models are trained locally and only parameters are shared
- **Secure contexts**: Collaborative contexts implement access controls
- **Audit logging**: All knowledge transfers and collaborative activities are logged

## Configuration

Configuration is managed through `application.yml` with the following key settings:
- Server port: 8084
- Database: H2 in-memory database
- Collaboration API URL: http://collaboration-service:8083/api/v1
- Integration API URL: http://integration-service:8082/api/v1

## Deployment

The service can be deployed using Docker:

```bash
docker build -t lumina-ai/learning-service .
docker run -p 8084:8084 lumina-ai/learning-service
```

Or as part of the microservices stack using docker-compose.

## Development

Build the service using Maven:

```bash
mvn clean package
```

Run the service locally:

```bash
java -jar target/learning-service-0.0.1-SNAPSHOT.jar
```
