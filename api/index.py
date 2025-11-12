"""
Vercel serverless function handler for GitLab MCP Server
Note: MCP servers typically use stdio protocol. This HTTP handler is for 
health checks and metadata. For actual MCP communication, clients should 
connect via stdio (local) or use a bridge service.
"""

import os
import json
import sys

# Add parent directory to path to import server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from server import mcp, verify_bearer_token
except ImportError:
    mcp = None
    verify_bearer_token = None

def handler(request):
    """
    Vercel serverless function handler
    Provides health check and server metadata endpoint
    """
    from vercel import Response
    
    try:
        # Get request method and path
        method = request.method
        path = request.path if hasattr(request, 'path') else '/'
        
        # Get authorization header
        auth_header = None
        if hasattr(request, 'headers'):
            auth_header = request.headers.get('Authorization') or request.headers.get('authorization')
        elif hasattr(request, 'get_header'):
            auth_header = request.get_header('Authorization')
        
        # Verify bearer token (skip for OPTIONS)
        if method != "OPTIONS" and verify_bearer_token:
            if not verify_bearer_token(auth_header):
                return Response.json({
                    "error": "Unauthorized",
                    "message": "Valid bearer token required in Authorization header"
                }, status=401, headers={
                    "WWW-Authenticate": "Bearer"
                })
        
        # Handle CORS preflight
        if method == "OPTIONS":
            return Response.json({}, headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            })
        
        # Handle health check
        if path == "/" or path == "/health" or method == "GET":
            tools_list = []
            if mcp and hasattr(mcp, '_tools'):
                tools_list = list(mcp._tools.keys())
            elif mcp:
                # Try to get tools from FastMCP instance
                try:
                    tools_list = [name for name in dir(mcp) if not name.startswith('_')]
                except:
                    pass
            
            return Response.json({
                "status": "ok",
                "service": "GitLab MCP Server",
                "version": "1.0.0",
                "tools": tools_list,
                "note": "This server uses stdio protocol. For local use, run 'python server.py'"
            })
        
        return Response.json({"error": "Method not allowed"}, status=405)
        
    except Exception as e:
        return Response.json({"error": str(e)}, status=500)
