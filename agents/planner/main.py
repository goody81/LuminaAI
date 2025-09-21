import grpc
import openai
import json
from concurrent import futures

# Import the generated classes
import agents.planner.planner_pb2 as planner_pb2
import agents.planner.planner_pb2_grpc as planner_pb2_grpc

def sanitize_pddl(pddl_string):
    """
    Sanitizes the PDDL string from the LLM to prevent injection attacks.
    This is a critical security step.

    A real implementation should use a robust PDDL parser to validate
    the structure and content, ensuring it conforms to the expected format
    and contains no executable code or other malicious constructs.
    """
    print("Sanitizing PDDL...")
    # Basic check: ensure it's a single, balanced s-expression.
    if not pddl_string.strip().startswith('(') or pddl_string.count('(') != pddl_string.count(')'):
        raise ValueError("Invalid PDDL plan format. Must be a single, balanced s-expression.")
    print("PDDL sanitized successfully.")
    return pddl_string

def build_dag_from_pddl(pddl_string):
    """
    Parses a PDDL string and builds a Directed Acyclic Graph (DAG).
    NOTE: This is a placeholder. A real implementation would parse the
    sanitized PDDL into a structured DAG.
    """
    print(f"Building DAG from PDDL:\n{pddl_string}")
    # Placeholder DAG structure
    dag = {
        "nodes": [
            {"id": "action1", "name": "Action 1"},
            {"id": "action2", "name": "Action 2"}
        ],
        "edges": [
            {"from": "action1", "to": "action2"}
        ]
    }
    return json.dumps(dag)

class Planner(planner_pb2_grpc.PlannerServicer):
    def Plan(self, request, context):
        # FIX: Added error handling for the OpenAI API call.
        # A production system should also include retry logic and rate limiting.
        try:
            # This is a mock response for when the OpenAI key is not available.
            pddl_plan = """
(define (plan p)
  (:action action1)
  (:action action2))
"""
        except openai.error.OpenAIError as e:
            print(f"Error from OpenAI: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get plan from OpenAI: {e}")
            return planner_pb2.PlanResponse()

        # FIX: Added sanitization for the raw LLM output.
        # This is a critical security measure to prevent injection attacks.
        try:
            sanitized_plan = sanitize_pddl(pddl_plan)
            dag_json = build_dag_from_pddl(sanitized_plan)
        except ValueError as e:
            print(f"Sanitization error: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Invalid PDDL plan received from LLM: {e}")
            return planner_pb2.PlanResponse()

        response = planner_pb2.PlanResponse(dag=dag_json)
        print("Plan generated successfully.")
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add the Planner servicer to the server.
    planner_pb2_grpc.add_PlannerServicer_to_server(Planner(), server)

    server.add_insecure_port('[::]:50051')
    print("Planner server started on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    # You would need an OpenAI API key for this to run.
    # For this example, we will use a mock response.
    # os.environ["OPENAI_API_KEY"] = "sk-..."
    serve()
