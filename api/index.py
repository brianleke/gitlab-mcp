"""Vercel serverless function handler for GitLab MCP Server using BaseHTTPRequestHandler"""

import json
import os
from http.server import BaseHTTPRequestHandler

SERVER_BEARER_TOKEN = os.environ.get("SERVER_BEARER_TOKEN", "")

def verify_bearer_token(auth_header):
    """Verify bearer token authorization"""
    if not SERVER_BEARER_TOKEN:
        return True
    if not auth_header or not isinstance(auth_header, str):
        return False
    if not auth_header.startswith("Bearer "):
        return False
    return auth_header[7:].strip() == SERVER_BEARER_TOKEN

class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler inheriting from BaseHTTPRequestHandler"""
    
    def _process_request(self):
        """Process the request and return response data"""
        try:
            # Get authorization header
            auth_header = self.headers.get('Authorization') or self.headers.get('authorization')
            
            # Verify bearer token
            if not verify_bearer_token(auth_header):
                return {
                    'status': 401,
                    'headers': {'WWW-Authenticate': 'Bearer'},
                    'body': {
                        "error": "Unauthorized",
                        "message": "Valid bearer token required"
                    }
                }
            
            # Handle health check endpoint
            if self.path == "/" or self.path == "/health":
                response_data = {
                    "status": "ok",
                    "service": "GitLab MCP Server",
                    "version": "1.0.0",
                    "tools": [
                        "list_projects", "get_project", "create_project",
                        "list_issues", "get_issue", "create_issue", "update_issue",
                        "list_merge_requests", "get_merge_request", "create_merge_request", "update_merge_request",
                        "list_pipelines", "get_pipeline", "cancel_pipeline",
                        "list_branches", "get_branch",
                        "get_current_user", "list_users",
                        "list_groups", "get_group"
                    ],
                    "note": "This server uses stdio protocol. For local use, run 'python server.py'"
                }
                return {
                    'status': 200,
                    'headers': {},
                    'body': response_data
                }
            else:
                # 404 for unknown paths
                return {
                    'status': 404,
                    'headers': {},
                    'body': {
                        "error": "Not Found",
                        "message": f"Path {self.path} not found"
                    }
                }
                
        except Exception as e:
            # Handle errors
            return {
                'status': 500,
                'headers': {},
                'body': {
                    "error": str(e),
                    "type": type(e).__name__
                }
            }
    
    def _send_json_response(self, status, headers, body):
        """Helper to send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(json.dumps(body).encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests"""
        result = self._process_request()
        self._send_json_response(result['status'], result['headers'], result['body'])
    
    def do_POST(self):
        """Handle POST requests"""
        result = self._process_request()
        self._send_json_response(result['status'], result['headers'], result['body'])
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps({}).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to suppress default logging"""
        # Vercel handles logging, so we can suppress this
        pass
