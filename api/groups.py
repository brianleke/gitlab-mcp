"""
API endpoint for GitLab groups.
"""

import json
from gitlab_client import get_gitlab_client
from utils import json_response, error_response, cors_response, parse_request


def handler(request):
    """Handle groups API requests."""
    req = parse_request(request)
    
    # Handle CORS preflight
    if req["method"] == "OPTIONS":
        return cors_response()
    
    try:
        client = get_gitlab_client()
        
        if req["method"] == "GET":
            params = req["args"]
            search = params.get("search")
            limit = int(params.get("limit", 20))
            
            list_params = {}
            if search:
                list_params["search"] = search
            
            groups = client.groups.list(**list_params, get_all=False)
            groups = groups[:limit]
            
            result = [
                {
                    "id": g.id,
                    "name": g.name,
                    "path": g.path,
                    "full_path": g.full_path,
                    "web_url": g.web_url,
                    "description": g.description,
                }
                for g in groups
            ]
            return json_response(result)
        
        else:
            return error_response("Method not allowed", 405)
    
    except Exception as e:
        return error_response(str(e), 500)

