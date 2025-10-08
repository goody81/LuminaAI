"""
Health check service for LuminaAI Planner.

Provides a simple HTTP health check endpoint for Kubernetes liveness
and readiness probes.
"""
import http.server
import socketserver
import threading
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for health checks."""
    
    def do_GET(self):
        """Handle GET requests for health check."""
        if self.path == '/healthz' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy", "service": "planner"}')
        elif self.path == '/readyz' or self.path == '/ready':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ready", "service": "planner"}')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Override to use Python logging instead of stderr."""
        logger.debug("%s - %s" % (self.address_string(), format % args))


class HealthCheckServer:
    """Simple HTTP server for health checks."""
    
    def __init__(self, port: int = 8080):
        """
        Initialize the health check server.
        
        Args:
            port: Port to listen on (default: 8080)
        """
        self.port = port
        self.server: Optional[socketserver.TCPServer] = None
        self.thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start the health check server in a background thread."""
        try:
            self.server = socketserver.TCPServer(("", self.port), HealthCheckHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            logger.info(f"Health check server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")
    
    def stop(self):
        """Stop the health check server."""
        if self.server:
            self.server.shutdown()
            logger.info("Health check server stopped")
