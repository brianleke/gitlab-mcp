"""
Utility functions for API responses.
"""

import json
from typing import Any, Dict
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

