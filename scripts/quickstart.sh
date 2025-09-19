#!/bin/bash

# A script to quickly set up the BMAD environment.

echo "🚀 Starting BMAD quickstart..."

# Apply Kubernetes manifests
echo "Applying core manifests..."
kubectl apply -k clusters/bmad-prod/apps

# Wait for deployments to be ready
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=Available deployment/bmad-core -n bmad-prod --timeout=300s

# The review also mentioned this line:
# kubectl wait --for=condition=Succeeded taskrun --all -n bmad --timeout=120s
# I'll add it here. The review says it assumes Tekton.
echo "Waiting for initial task run to complete..."
kubectl wait --for=condition=Succeeded taskrun --all -n bmad --timeout=120s

echo "✅ BMAD environment is ready."
echo "Forwarding Grafana port to localhost:3000..."

# This command will run in the background
kubectl port-forward svc/grafana 3000:3000 -n bmad >/dev/null 2>&1 &
PORT_FORWARD_PID=$!

echo "Grafana is now accessible at http://localhost:3000"
echo "Port forwarding is running in the background with PID: $PORT_FORWARD_PID"
echo "To stop it, run: kill $PORT_FORWARD_PID"
echo "Quickstart script finished."
