"""
API endpoint for GitLab user information.
"""

import json
from gitlab_client import get_gitlab_client
from utils import json_response, error_response, cors_response, parse_request


def handler(request):
    """Handle user API requests."""
    req = parse_request(request)
    
    # Handle CORS preflight
    if req["method"] == "OPTIONS":
        return cors_response()
    
    try:
        client = get_gitlab_client()
        
        if req["method"] == "GET":
            user = client.user
            
            result = {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "web_url": user.web_url,
            }
            return json_response(result)
        
        else:
            return error_response("Method not allowed", 405)
    
    except Exception as e:
        return error_response(str(e), 500)

