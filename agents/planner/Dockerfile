# Multi-stage build for smaller, more secure images
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

# Set metadata labels
LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.title="LuminaAI Planner" \
      org.opencontainers.image.description="AI-powered planning service for multi-agent orchestration" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.vendor="BMAD AI" \
      org.opencontainers.image.licenses="MIT"

# Set the working directory
WORKDIR /usr/src/app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY agents/planner/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash planner

WORKDIR /usr/src/app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/planner/.local

# Copy application code
COPY agents/ /usr/src/app/agents

# Set environment variables
ENV PYTHONPATH=/usr/src/app \
    PYTHONUNBUFFERED=1 \
    PATH=/home/planner/.local/bin:$PATH \
    GRPC_PORT=50051 \
    HEALTH_PORT=8080 \
    LOG_LEVEL=INFO

# Switch to non-root user
USER planner

# Expose ports
EXPOSE 50051 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import http.client; conn = http.client.HTTPConnection('localhost', 8080); conn.request('GET', '/healthz'); r = conn.getresponse(); exit(0 if r.status == 200 else 1)"

# Run the service
CMD ["python", "-m", "agents.planner.main"]
