"""
Utility functions for API responses.
"""

import json
import os
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs


def send_response(handler, status_code: int, data: Any, cors: bool = True):
    """Send a JSON response using BaseHTTPRequestHandler."""
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json')
    if cors:
        handler.send_header('Access-Control-Allow-Origin', '*')
        handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        handler.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    handler.end_headers()
    
    response_body = json.dumps(data, indent=2, default=str).encode('utf-8')
    handler.wfile.write(response_body)


def parse_query_string(path: str) -> Dict[str, str]:
    """Parse query string from path."""
    parsed = urlparse(path)
    query_params = parse_qs(parsed.query)
    # Convert lists to single values
    return {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}


def read_request_body(handler) -> Dict[str, Any]:
    """Read and parse request body."""
    content_length = int(handler.headers.get('Content-Length', 0))
    if content_length == 0:
        return {}
    
    body = handler.rfile.read(content_length).decode('utf-8')
    try:
        return json.loads(body)
    except:
        return {}


def extract_bearer_token(handler) -> Optional[str]:
    """Extract Bearer token from Authorization header."""
    auth_header = handler.headers.get('Authorization', '')
    if not auth_header:
        return None
    
    # Check if it's a Bearer token
    if auth_header.startswith('Bearer '):
        return auth_header[7:].strip()
    
    return None


def validate_token(token: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate the bearer token.
    Returns (is_valid, error_message)
    """
    if not token:
        return False, "Missing Authorization header. Please provide a Bearer token."
    
    # Get allowed tokens from environment
    # Can be a single token or comma-separated list
    allowed_tokens = os.getenv('API_BEARER_TOKENS', '')
    
    # If no tokens configured, use GitLab token as fallback (for backward compatibility)
    if not allowed_tokens:
        gitlab_token = os.getenv('GITLAB_TOKEN', '')
        if gitlab_token:
            allowed_tokens = gitlab_token
        else:
            # If no tokens configured at all, allow any token (not recommended for production)
            # In production, you should set API_BEARER_TOKENS
            return True, None
    
    # Check if token is in allowed list
    allowed_list = [t.strip() for t in allowed_tokens.split(',') if t.strip()]
    
    if token in allowed_list:
        return True, None
    
    return False, "Invalid or unauthorized token."


def require_auth(handler) -> Tuple[bool, Optional[str]]:
    """
    Check if request is authenticated.
    Returns (is_authenticated, error_message)
    """
    token = extract_bearer_token(handler)
    is_valid, error = validate_token(token)
    
    if not is_valid:
        return False, error
    
    return True, None

