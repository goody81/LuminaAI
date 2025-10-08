"""
Example client for LuminaAI Planner service.

This demonstrates how to use the Planner gRPC API to generate
AI-powered execution plans.
"""
import grpc
import json
import sys
import time
from typing import Dict, Any

# Import the generated classes
sys.path.insert(0, '..')
from agents.planner import planner_pb2, planner_pb2_grpc


class PlannerClient:
    """Client for the LuminaAI Planner service."""

    def __init__(self, host: str = 'localhost', port: int = 50051):
        """
        Initialize the Planner client.

        Args:
            host: gRPC server host
            port: gRPC server port
        """
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = planner_pb2_grpc.PlannerStub(self.channel)
        print(f"Connected to Planner service at {host}:{port}")

    def generate_plan(self, prompt: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Generate an execution plan from a natural language prompt.

        Args:
            prompt: Natural language description of the task
            timeout: Request timeout in seconds

        Returns:
            Dictionary containing the generated DAG

        Raises:
            grpc.RpcError: If the request fails
        """
        request = planner_pb2.PlanRequest(prompt=prompt)

        try:
            print(f"\n📝 Prompt: {prompt}")
            print("🔄 Generating plan...")

            start_time = time.time()
            response = self.stub.Plan(request, timeout=timeout)
            elapsed = time.time() - start_time

            print(f"✅ Plan generated in {elapsed:.2f}s")

            # Parse the DAG JSON
            dag = json.loads(response.dag)
            return dag

        except grpc.RpcError as e:
            print(f"❌ Error: {e.code()}: {e.details()}")
            raise

    def print_plan(self, dag: Dict[str, Any]):
        """
        Pretty print a plan DAG.

        Args:
            dag: The DAG dictionary to print
        """
        print("\n" + "=" * 60)
        print("EXECUTION PLAN")
        print("=" * 60)

        # Print metadata
        metadata = dag.get('metadata', {})
        print(f"\nMetadata:")
        print(f"  Version: {metadata.get('version', 'N/A')}")
        print(f"  Created by: {metadata.get('created_by', 'N/A')}")
        print(f"  Nodes: {metadata.get('node_count', 0)}")
        print(f"  Edges: {metadata.get('edge_count', 0)}")

        # Print nodes
        print(f"\nNodes:")
        for i, node in enumerate(dag.get('nodes', []), 1):
            print(f"  {i}. {node['name']} (ID: {node['id']})")
            print(f"     Type: {node.get('type', 'N/A')}")
            print(f"     Status: {node.get('status', 'N/A')}")

        # Print edges
        print(f"\nEdges:")
        for i, edge in enumerate(dag.get('edges', []), 1):
            print(f"  {i}. {edge['from']} → {edge['to']} ({edge.get('type', 'sequential')})")

        print("=" * 60 + "\n")

    def close(self):
        """Close the gRPC channel."""
        self.channel.close()
        print("Connection closed")


def main():
    """Main function demonstrating the Planner client."""
    # Create client
    client = PlannerClient()

    try:
        # Example: Simple deployment plan
        print("\n" + "=" * 60)
        print("Example: Web Application Deployment")
        print("=" * 60)

        dag = client.generate_plan(
            "Deploy a web application with a database backend"
        )
        client.print_plan(dag)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        return 1
    finally:
        client.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())
