"""
Vercel serverless function handler for GitLab MCP Server
Note: MCP servers typically use stdio protocol. This HTTP handler is for 
health checks and metadata. For actual MCP communication, clients should 
connect via stdio (local) or use a bridge service.
"""

import os
import json
import sys

# Server bearer token for authorization
SERVER_BEARER_TOKEN = os.getenv("SERVER_BEARER_TOKEN", "")

def verify_bearer_token(authorization_header):
    """
    Verify bearer token authorization
    
    Args:
        authorization_header: Authorization header value (e.g., "Bearer token123")
    
    Returns:
        True if token is valid or no token is required, False otherwise
    """
    # If no server token is configured, allow access (backward compatible)
    if not SERVER_BEARER_TOKEN:
        return True
    
    # If token is configured, require valid bearer token
    if not authorization_header:
        return False
    
    # Extract token from "Bearer <token>" format
    if not authorization_header.startswith("Bearer "):
        return False
    
    token = authorization_header[7:].strip()  # Remove "Bearer " prefix
    return token == SERVER_BEARER_TOKEN

# Try to import server module (may fail if dependencies aren't available)
mcp = None
tools_list = []
import_error = None
try:
    # Add parent directory to path to import server
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from server import mcp as server_mcp
    mcp = server_mcp
    # Try to get tools list
    if hasattr(mcp, '_tools'):
        tools_list = list(mcp._tools.keys())
except Exception as e:
    # If import fails, continue without it
    import_error = str(e)
    tools_list = []

def create_response(body, status_code=200, headers=None):
    """Create a Vercel-compatible response"""
    if headers is None:
        headers = {}
    
    # Ensure Content-Type is set
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(body) if isinstance(body, dict) else str(body)
    }

def handler(request):
    """
    Vercel serverless function handler
    Provides health check and server metadata endpoint
    """
    try:
        # Handle None or missing request
        if request is None:
            request = {}
        
        # Get request method
        if isinstance(request, dict):
            method = request.get('method', 'GET')
            path = request.get('path', '/')
            headers = request.get('headers', {}) or {}
        else:
            method = getattr(request, 'method', 'GET')
            path = getattr(request, 'path', '/')
            headers = getattr(request, 'headers', {}) or {}
        
        # Get authorization header (case-insensitive)
        auth_header = None
        for key, value in headers.items():
            if key.lower() == 'authorization':
                auth_header = value
                break
        
        # Verify bearer token (skip for OPTIONS)
        if method != "OPTIONS":
            if not verify_bearer_token(auth_header):
                return create_response(
                    {
                        "error": "Unauthorized",
                        "message": "Valid bearer token required in Authorization header"
                    },
                    status_code=401,
                    headers={
                        "WWW-Authenticate": "Bearer",
                        "Access-Control-Allow-Origin": "*"
                    }
                )
        
        # Handle CORS preflight
        if method == "OPTIONS":
            return create_response(
                {},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                }
            )
        
        # Handle health check
        if path == "/" or path == "/health" or method == "GET":
            response_body = {
                "status": "ok",
                "service": "GitLab MCP Server",
                "version": "1.0.0",
                "tools": tools_list if tools_list else [
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
            
            if import_error:
                response_body["warning"] = f"Server module import failed: {import_error}"
            
            return create_response(response_body)
        
        return create_response(
            {"error": "Method not allowed"},
            status_code=405
        )
        
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "type": type(e).__name__
        }
        # Include traceback in development
        if os.getenv("VERCEL_ENV") != "production":
            error_details["traceback"] = traceback.format_exc()
        
        return create_response(
            error_details,
            status_code=500
        )
