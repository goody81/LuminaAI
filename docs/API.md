# LuminaAI API Documentation

## Overview

LuminaAI provides a gRPC-based API for AI-powered planning and orchestration. This document describes the available services, methods, and message formats.

## Base URL

```
grpc://planner.bmad-prod.svc.cluster.local:50051
```

For local development:
```
grpc://localhost:50051
```

## Authentication

Currently, the API is unauthenticated. Authentication will be added in a future release.

## Services

### Planner Service

The Planner service provides AI-powered planning capabilities using PDDL and Large Language Models.

#### Plan

Generates an execution plan based on a natural language prompt.

**Method:** `planner.Planner/Plan`

**Request:**

```protobuf
message PlanRequest {
  string prompt = 1;
}
```

**Response:**

```protobuf
message PlanResponse {
  string dag = 1;  // JSON-encoded DAG
}
```

**Example Request (grpcurl):**

```bash
grpcurl -plaintext -d '{"prompt": "Create a plan to deploy a web application"}' \
  localhost:50051 planner.Planner/Plan
```

**Example Response:**

```json
{
  "dag": "{\"nodes\":[{\"id\":\"action1\",\"name\":\"Initialize\",\"type\":\"action\",\"status\":\"pending\"},{\"id\":\"action2\",\"name\":\"Deploy\",\"type\":\"action\",\"status\":\"pending\"},{\"id\":\"action3\",\"name\":\"Verify\",\"type\":\"action\",\"status\":\"pending\"}],\"edges\":[{\"from\":\"action1\",\"to\":\"action2\",\"type\":\"sequential\"},{\"from\":\"action2\",\"to\":\"action3\",\"type\":\"sequential\"}],\"metadata\":{\"version\":\"1.0\",\"created_by\":\"LuminaAI Planner\",\"node_count\":3,\"edge_count\":2}}"
}
```

**DAG Structure:**

The returned DAG is a JSON object with the following structure:

```json
{
  "nodes": [
    {
      "id": "string",      // Unique node identifier
      "name": "string",    // Human-readable name
      "type": "string",    // Node type (e.g., "action")
      "status": "string"   // Execution status ("pending", "running", "completed", "failed")
    }
  ],
  "edges": [
    {
      "from": "string",    // Source node ID
      "to": "string",      // Target node ID
      "type": "string"     // Edge type (e.g., "sequential", "parallel")
    }
  ],
  "metadata": {
    "version": "string",
    "created_by": "string",
    "node_count": number,
    "edge_count": number
  }
}
```

## Error Handling

### gRPC Status Codes

- `OK` (0): Success
- `INVALID_ARGUMENT` (3): Invalid PDDL or prompt
- `INTERNAL` (13): Internal server error (e.g., LLM API failure)
- `UNAVAILABLE` (14): Service temporarily unavailable

### Error Response Example

```json
{
  "code": 3,
  "message": "Invalid PDDL plan received from LLM: Unbalanced parentheses: 5 opening, 4 closing",
  "details": []
}
```

## Rate Limits

No rate limits are currently enforced. Rate limiting will be added in a future release.

Recommended client-side rate limits:
- 100 requests per minute per client
- Exponential backoff on errors

## Health Checks

### HTTP Health Endpoint

**Endpoint:** `GET /healthz`  
**Port:** 8080

**Response:**

```json
{
  "status": "healthy",
  "service": "planner"
}
```

### HTTP Readiness Endpoint

**Endpoint:** `GET /readyz`  
**Port:** 8080

**Response:**

```json
{
  "status": "ready",
  "service": "planner"
}
```

## Client Libraries

### Python

```python
import grpc
from agents.planner import planner_pb2, planner_pb2_grpc

# Create a gRPC channel
channel = grpc.insecure_channel('localhost:50051')
stub = planner_pb2_grpc.PlannerStub(channel)

# Make a request
request = planner_pb2.PlanRequest(prompt="Deploy a web application")
response = stub.Plan(request)

# Parse the response
import json
dag = json.loads(response.dag)
print(f"Generated plan with {dag['metadata']['node_count']} nodes")
```

### Using grpcurl

```bash
# Install grpcurl
brew install grpcurl  # macOS
apt-get install grpcurl  # Ubuntu/Debian

# List available services
grpcurl -plaintext localhost:50051 list

# Describe a service
grpcurl -plaintext localhost:50051 describe planner.Planner

# Make a request
grpcurl -plaintext -d '{"prompt": "Your task here"}' \
  localhost:50051 planner.Planner/Plan
```

### Using curl (via grpc-gateway, planned)

```bash
curl -X POST http://localhost:8080/v1/plan \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Deploy a web application"}'
```

## Best Practices

### 1. Connection Management

- Reuse gRPC channels when possible
- Set appropriate timeouts
- Implement connection pooling for high-load scenarios

```python
# Good: Reuse channel
channel = grpc.insecure_channel('localhost:50051')
stub = planner_pb2_grpc.PlannerStub(channel)
for prompt in prompts:
    response = stub.Plan(planner_pb2.PlanRequest(prompt=prompt))

# Bad: Create new channel per request
for prompt in prompts:
    channel = grpc.insecure_channel('localhost:50051')
    stub = planner_pb2_grpc.PlannerStub(channel)
    response = stub.Plan(planner_pb2.PlanRequest(prompt=prompt))
    channel.close()
```

### 2. Error Handling

Always implement proper error handling:

```python
try:
    response = stub.Plan(request, timeout=30)
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
        print(f"Invalid request: {e.details()}")
    elif e.code() == grpc.StatusCode.UNAVAILABLE:
        print("Service unavailable, retrying...")
        # Implement retry logic
    else:
        print(f"Unexpected error: {e}")
```

### 3. Timeouts

Set appropriate timeouts based on your use case:

```python
# Default timeout: 30 seconds
response = stub.Plan(request, timeout=30)

# For complex plans, increase timeout
response = stub.Plan(request, timeout=120)
```

### 4. Streaming (Planned)

Future versions will support streaming for long-running operations:

```python
# Streaming plan generation (planned)
for update in stub.PlanStream(request):
    print(f"Progress: {update.progress}%")
    if update.completed:
        dag = json.loads(update.dag)
```

## Versioning

The API follows semantic versioning. Breaking changes will result in a new major version.

Current version: **v1.0.0**

## Changelog

### v1.0.0 (2024-10-01)

- Initial release
- Plan generation with PDDL
- DAG output format
- Health check endpoints
- gRPC API

## Support

- **Documentation**: https://github.com/goody81/LuminaAI/tree/main/docs
- **Issues**: https://github.com/goody81/LuminaAI/issues
- **Discussions**: https://github.com/goody81/LuminaAI/discussions

## License

MIT License - see [LICENSE](../LICENSE) file for details.
