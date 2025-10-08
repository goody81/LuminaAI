# LuminaAI - BMAD Neural Core

> Next-generation planet-scale multi-agent AI system

[![CI](https://img.shields.io/github/actions/workflow/status/goody81/LuminaAI/00-bootstrap.yml?branch=main)](https://github.com/goody81/LuminaAI/actions)
[![License](https://img.shields.io/github/license/goody81/LuminaAI)](https://github.com/goody81/LuminaAI/blob/main/LICENSE)
[![Stars](https://img.shields.io/github/stars/goody81/LuminaAI)](https://github.com/goody81/LuminaAI/stargazers)

## Overview

LuminaAI is the core repository for the BMAD (Bursty, Multi-Agent, Deterministic) Neural Core - a production-ready, cloud-native multi-agent AI orchestration platform designed for 2027 and beyond.

### Key Features

- 🧠 **Intelligent Planning**: Advanced PDDL-based planning with LLM integration
- 🔄 **Multi-Agent Orchestration**: Coordinate multiple AI agents for complex tasks
- 🚀 **Cloud-Native**: Built on Kubernetes with GitOps (Flux) for zero-downtime deployments
- 📊 **Enterprise Observability**: Comprehensive monitoring with Prometheus and Grafana
- 🔒 **Security First**: Built-in sanitization, secret management, and secure-by-default architecture
- ⚡ **High Performance**: gRPC-based microservices architecture for low-latency communication
- 🔧 **Production Ready**: Health checks, metrics, logging, and automated CI/CD

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     LuminaAI Platform                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────┐       ┌──────────┐       ┌──────────┐    │
│  │  Planner │◄─────►│  Executor│◄─────►│  Monitor │    │
│  │  Agent   │       │  Agent   │       │  Agent   │    │
│  └────┬─────┘       └────┬─────┘       └────┬─────┘    │
│       │                  │                   │          │
│       └──────────────┬───┴───────────────────┘          │
│                      │                                   │
│              ┌───────▼────────┐                         │
│              │  Orchestrator  │                         │
│              └───────┬────────┘                         │
│                      │                                   │
├──────────────────────┼───────────────────────────────────┤
│  Infrastructure      │                                   │
│                      │                                   │
│  ┌─────────┐  ┌─────▼─────┐  ┌──────────┐             │
│  │Prometheus│◄─┤Kubernetes │─►│  Grafana │             │
│  └─────────┘  └───────────┘  └──────────┘             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Kubernetes cluster (for production deployment)
- kubectl

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/goody81/LuminaAI.git
   cd LuminaAI
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r agents/planner/requirements.txt
   ```

3. **Run the planner service**
   ```bash
   export PYTHONPATH=$(pwd)
   python -m agents.planner.main
   ```

4. **Test the service** (in another terminal)
   ```bash
   # Install grpcurl for testing
   # brew install grpcurl  # macOS
   # apt-get install grpcurl  # Ubuntu/Debian
   
   grpcurl -plaintext -d '{"prompt": "Plan a task"}' \
     localhost:50051 planner.Planner/Plan
   ```

### Docker Deployment

```bash
# Build the planner image
docker build -t luminaai/planner:latest -f agents/planner/Dockerfile .

# Run with docker
docker run -p 50051:50051 luminaai/planner:latest
```

### Kubernetes Deployment

```bash
# Run the quickstart script
./scripts/quickstart.sh

# Or manually:
kubectl create namespace bmad-prod
kubectl apply -k clusters/bmad-prod/apps

# Access Grafana dashboard
kubectl port-forward svc/kube-prometheus-stack-grafana 3000:3000 -n bmad-prod
# Navigate to http://localhost:3000
```

## Project Structure

```
LuminaAI/
├── agents/
│   └── planner/           # Planner microservice
│       ├── main.py        # gRPC service implementation
│       ├── planner.proto  # Protocol buffer definitions
│       ├── Dockerfile     # Container image
│       └── requirements.txt
├── clusters/
│   └── bmad-prod/         # Production Kubernetes manifests
│       └── apps/
│           ├── planner.yaml    # Planner deployment
│           └── monitoring.yaml # Prometheus/Grafana setup
├── scripts/
│   └── quickstart.sh      # Quick deployment script
├── tekton/                # CI/CD pipeline definitions
│   ├── pylint-task.yaml
│   └── pylint-taskrun.yaml
└── README.md

```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-grpc

# Run tests
pytest tests/ -v --cov=agents
```

### Code Quality

```bash
# Install linting tools
pip install pylint black isort mypy

# Format code
black agents/
isort agents/

# Type checking
mypy agents/

# Linting
pylint agents/
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - OpenAI API key for LLM integration
- `GRPC_PORT` - gRPC server port (default: 50051)
- `LOG_LEVEL` - Logging level (default: INFO)

### Kubernetes Secrets

For production deployments, create required secrets:

```bash
# Grafana admin credentials
kubectl create secret generic grafana-admin-credentials \
  --from-literal=admin-user=admin \
  --from-literal=admin-password=<your-secure-password> \
  -n bmad-prod

# OpenAI API key
kubectl create secret generic openai-credentials \
  --from-literal=api-key=<your-api-key> \
  -n bmad-prod
```

## Monitoring & Observability

- **Metrics**: Exposed via Prometheus metrics endpoint
- **Logs**: Structured JSON logging to stdout
- **Tracing**: Distributed tracing with OpenTelemetry (coming soon)
- **Dashboards**: Pre-configured Grafana dashboards

Access Grafana at `http://localhost:3000` after port-forwarding.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Security

See [SECURITY.md](SECURITY.md) for our security policy and how to report vulnerabilities.

## Roadmap

- [x] Core planner agent with gRPC interface
- [x] Kubernetes deployment with monitoring
- [x] CI/CD with GitHub Actions and Tekton
- [ ] Multi-agent orchestration
- [ ] Advanced reasoning and reflection
- [ ] Distributed tracing
- [ ] Multi-LLM provider support
- [ ] API gateway and authentication
- [ ] Web UI for management
- [ ] Horizontal pod autoscaling
- [ ] Advanced caching layer

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [gRPC](https://grpc.io/)
- Orchestrated on [Kubernetes](https://kubernetes.io/)
- Monitored with [Prometheus](https://prometheus.io/) & [Grafana](https://grafana.com/)
- Powered by [OpenAI](https://openai.com/)

---

**LuminaAI** - Building the future of multi-agent AI, one agent at a time. 🚀

For questions, reach out to the team at hello@bmad.ai
