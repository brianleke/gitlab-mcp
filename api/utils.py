"""
Utility functions for API responses.
"""

import json
from typing import Any, Dict


def json_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Create a JSON response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
        "body": json.dumps(data, indent=2, default=str)
    }


def error_response(message: str, status_code: int = 400) -> Dict[str, Any]:
    """Create an error response."""
    return json_response({"error": message}, status_code)


def cors_response() -> Dict[str, Any]:
    """Create a CORS preflight response."""
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
        "body": ""
    }


def parse_request(request) -> Dict[str, Any]:
    """Parse Vercel request object into a normalized format."""
    # Handle different request formats
    if isinstance(request, dict):
        method = request.get("method", "GET")
        query = request.get("query", {}) or {}
        body = request.get("body", "")
    else:
        # Fallback for different request object types
        method = getattr(request, "method", "GET") if hasattr(request, "method") else "GET"
        query = getattr(request, "query", {}) if hasattr(request, "query") else {}
        body = getattr(request, "body", "") if hasattr(request, "body") else ""
    
    # Parse JSON body if present
    parsed_body = {}
    if body:
        try:
            parsed_body = json.loads(body) if isinstance(body, str) else body
        except:
            parsed_body = {}
    
    return {
        "method": method,
        "args": query,
        "body": parsed_body,
        "raw_body": body
    }

