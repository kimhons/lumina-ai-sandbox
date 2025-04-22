# Deployment Guide for Lumina AI

This guide provides instructions for deploying Lumina AI in various environments.

## Prerequisites

- Docker and Docker Compose (v1.29.0+)
- Kubernetes (v1.20+) for production deployments
- API keys for AI providers (OpenAI, Claude, Gemini, DeepSeek, Grok)
- Minimum 8GB RAM, 4 CPU cores recommended

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# AI Provider API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
GROK_API_KEY=your_grok_api_key

# Security Keys (generate with openssl rand -base64 32)
LUMINA_AUTH_SECRET=your_auth_secret_key
LUMINA_ENCRYPTION_KEY=your_encryption_key

# Optional Vector DB Configuration
VECTOR_DB_HOST=your_vector_db_host
VECTOR_DB_PORT=your_vector_db_port
```

## Local Development Deployment

For local development and testing:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Production Deployment

### Docker Compose (Single Server)

For small to medium deployments on a single server:

```bash
# Production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

For scalable production deployments:

1. Apply the Kubernetes configurations:

```bash
kubectl apply -f deployment/k8s/namespace.yaml
kubectl apply -f deployment/k8s/secrets.yaml  # After adding your secrets
kubectl apply -f deployment/k8s/configmaps.yaml
kubectl apply -f deployment/k8s/services/
kubectl apply -f deployment/k8s/deployments/
```

2. Verify the deployment:

```bash
kubectl get pods -n lumina-ai
```

## Scaling Considerations

- **Core Service**: Scale based on API request load
- **Providers Service**: Scale based on AI request volume
- **Memory Service**: Scale based on memory usage and retrieval operations
- **Security Service**: Scale based on authentication/authorization load
- **Web UI**: Scale based on user traffic

## Monitoring

Prometheus and Grafana configurations are provided in the `deployment/monitoring` directory.

```bash
# Deploy monitoring stack
docker-compose -f deployment/monitoring/docker-compose.yml up -d
```

## Backup and Recovery

Regular backups of the following volumes are recommended:

- `core_data`
- `providers_data`
- `memory_data`
- `security_data`

Backup script is available at `deployment/scripts/backup.sh`.

## Troubleshooting

Common issues and solutions:

1. **Connection errors between services**: Check network configuration and ensure services can communicate
2. **API key errors**: Verify environment variables are correctly set
3. **Performance issues**: Check resource allocation and consider scaling the affected services

For more detailed troubleshooting, check the logs:

```bash
docker-compose logs -f service_name
```

## Upgrading

To upgrade to a new version:

```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

For zero-downtime upgrades in Kubernetes:

```bash
kubectl apply -f deployment/k8s/deployments/
```
