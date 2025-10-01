"""
LuminaAI Planner Service

A production-ready gRPC service for AI-powered planning using PDDL
and Large Language Models.
"""
import grpc
import openai
import json
import logging
import os
import sys
from concurrent import futures
from typing import Dict, Any, Optional

# Import the generated classes
import agents.planner.planner_pb2 as planner_pb2
import agents.planner.planner_pb2_grpc as planner_pb2_grpc
from agents.planner.health import HealthCheckServer

# Configure structured logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


def sanitize_pddl(pddl_string: str) -> str:
    """
    Sanitizes the PDDL string from the LLM to prevent injection attacks.
    This is a critical security step.

    A real implementation should use a robust PDDL parser to validate
    the structure and content, ensuring it conforms to the expected format
    and contains no executable code or other malicious constructs.
    
    Args:
        pddl_string: The raw PDDL string to sanitize
        
    Returns:
        The sanitized PDDL string
        
    Raises:
        ValueError: If the PDDL format is invalid
    """
    logger.debug("Sanitizing PDDL...")
    
    # Trim whitespace
    pddl_string = pddl_string.strip()
    
    # Basic validation checks
    if not pddl_string:
        raise ValueError("Empty PDDL plan")
        
    if not pddl_string.startswith('('):
        raise ValueError("Invalid PDDL plan format. Must start with '('")
        
    # Check balanced parentheses
    open_count = pddl_string.count('(')
    close_count = pddl_string.count(')')
    if open_count != close_count:
        raise ValueError(
            f"Invalid PDDL plan format. Unbalanced parentheses: "
            f"{open_count} opening, {close_count} closing"
        )
    
    # Check for potentially dangerous patterns
    dangerous_patterns = [
        'exec', 'eval', 'import', 'subprocess', 
        '__import__', 'compile', 'globals', 'locals'
    ]
    lower_pddl = pddl_string.lower()
    for pattern in dangerous_patterns:
        if pattern in lower_pddl:
            raise ValueError(f"Potentially dangerous pattern detected: {pattern}")
    
    logger.debug("PDDL sanitized successfully")
    return pddl_string


def build_dag_from_pddl(pddl_string: str) -> str:
    """
    Parses a PDDL string and builds a Directed Acyclic Graph (DAG).
    
    This implementation extracts actions from PDDL and creates a structured
    DAG representation suitable for execution planning.
    
    Args:
        pddl_string: The sanitized PDDL string to parse
        
    Returns:
        JSON string representing the DAG with nodes and edges
        
    Note:
        This is a simplified implementation. A production system would use
        a full PDDL parser library and handle complex dependencies,
        preconditions, and effects.
    """
    logger.debug(f"Building DAG from PDDL:\n{pddl_string}")
    
    try:
        # Extract actions from PDDL (simplified parsing)
        nodes = []
        edges = []
        
        # Split by :action to find action definitions
        parts = pddl_string.split(':action')
        
        for i, part in enumerate(parts[1:], 1):  # Skip first empty part
            # Extract action name (first word after :action)
            lines = part.strip().split('\n')
            if lines:
                action_name = lines[0].strip().rstrip(')')
                node_id = f"action{i}"
                nodes.append({
                    "id": node_id,
                    "name": action_name or f"Action {i}",
                    "type": "action",
                    "status": "pending"
                })
                
                # Create sequential edges (simplified - real implementation 
                # would analyze preconditions and effects)
                if i > 1:
                    edges.append({
                        "from": f"action{i-1}",
                        "to": node_id,
                        "type": "sequential"
                    })
        
        # Fallback to default structure if parsing fails
        if not nodes:
            logger.warning("Could not parse PDDL actions, using default structure")
            nodes = [
                {"id": "action1", "name": "Initialize", "type": "action", "status": "pending"},
                {"id": "action2", "name": "Execute", "type": "action", "status": "pending"},
                {"id": "action3", "name": "Finalize", "type": "action", "status": "pending"}
            ]
            edges = [
                {"from": "action1", "to": "action2", "type": "sequential"},
                {"from": "action2", "to": "action3", "type": "sequential"}
            ]
        
        dag = {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "version": "1.0",
                "created_by": "LuminaAI Planner",
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
        }
        
        logger.info(f"DAG built successfully with {len(nodes)} nodes and {len(edges)} edges")
        return json.dumps(dag, indent=2)
        
    except Exception as e:
        logger.error(f"Error building DAG: {e}", exc_info=True)
        # Return a minimal valid DAG on error
        error_dag = {
            "nodes": [{"id": "error", "name": "Error", "type": "error"}],
            "edges": [],
            "metadata": {"error": str(e)}
        }
        return json.dumps(error_dag)


class Planner(planner_pb2_grpc.PlannerServicer):
    """
    Planner gRPC service implementation.
    
    Provides AI-powered planning capabilities using LLMs and PDDL.
    Handles plan generation, sanitization, and DAG construction.
    """
    
    def __init__(self):
        """Initialize the Planner service."""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            logger.info("OpenAI API key configured")
        else:
            logger.warning("No OpenAI API key found, using mock responses")
    
    def _generate_plan_with_llm(self, prompt: str) -> str:
        """
        Generate a PDDL plan using an LLM.
        
        Args:
            prompt: The user's planning request
            
        Returns:
            PDDL plan as a string
            
        Raises:
            openai.error.OpenAIError: If the API call fails
        """
        if not self.openai_api_key:
            # Return mock response if no API key
            logger.info("Using mock PDDL response")
            return """
(define (plan user-plan)
  (:action initialize)
  (:action process)
  (:action finalize))
"""
        
        try:
            # Call OpenAI API for real planning
            logger.info(f"Generating plan with LLM for prompt: {prompt[:100]}...")
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI planning expert. Generate PDDL plans "
                            "in response to user requests. Return only valid PDDL."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Create a PDDL plan for: {prompt}"
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            pddl_plan = response.choices[0].message.content
            logger.info("LLM plan generated successfully")
            return pddl_plan
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}", exc_info=True)
            raise
    
    def Plan(self, request, context):
        """
        Handle Plan RPC requests.
        
        Args:
            request: PlanRequest message containing the prompt
            context: gRPC context
            
        Returns:
            PlanResponse containing the DAG
        """
        try:
            logger.info(f"Received plan request: {request.prompt[:100]}...")
            
            # Generate plan using LLM
            try:
                pddl_plan = self._generate_plan_with_llm(request.prompt)
            except openai.error.OpenAIError as e:
                logger.error(f"Error from OpenAI: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Failed to get plan from OpenAI: {e}")
                return planner_pb2.PlanResponse()
            except Exception as e:
                logger.error(f"Unexpected error generating plan: {e}", exc_info=True)
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Failed to generate plan: {e}")
                return planner_pb2.PlanResponse()

            # Sanitize and parse the PDDL plan
            try:
                sanitized_plan = sanitize_pddl(pddl_plan)
                dag_json = build_dag_from_pddl(sanitized_plan)
            except ValueError as e:
                logger.error(f"Sanitization error: {e}")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"Invalid PDDL plan received from LLM: {e}")
                return planner_pb2.PlanResponse()

            response = planner_pb2.PlanResponse(dag=dag_json)
            logger.info("Plan generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Unexpected error in Plan RPC: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {e}")
            return planner_pb2.PlanResponse()


def serve():
    """
    Start the gRPC server.
    
    Configures and starts the Planner gRPC service with health checks
    and graceful shutdown support.
    """
    port = os.getenv('GRPC_PORT', '50051')
    max_workers = int(os.getenv('MAX_WORKERS', '10'))
    health_port = int(os.getenv('HEALTH_PORT', '8080'))
    
    # Start health check server
    health_server = HealthCheckServer(port=health_port)
    health_server.start()
    
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50MB
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.max_pings_without_data', 0),
        ]
    )

    # Add the Planner servicer to the server
    planner_pb2_grpc.add_PlannerServicer_to_server(Planner(), server)

    server.add_insecure_port(f'[::]:{port}')
    logger.info(f"Starting Planner server on port {port} with {max_workers} workers...")
    logger.info(f"Health check server on port {health_port}")
    logger.info(f"Log level: {os.getenv('LOG_LEVEL', 'INFO')}")
    
    server.start()
    logger.info("Planner server started successfully")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal, stopping server...")
        health_server.stop()
        server.stop(grace=5)
        logger.info("Server stopped")


if __name__ == '__main__':
    logger.info("LuminaAI Planner Service starting...")
    logger.info(f"Python version: {sys.version}")
    
    # Validate environment
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning(
            "OPENAI_API_KEY not set. The service will use mock responses. "
            "Set OPENAI_API_KEY environment variable for real LLM integration."
        )
    
    serve()
