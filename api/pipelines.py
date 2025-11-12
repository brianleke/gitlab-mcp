"""
API endpoint for GitLab pipelines.
"""

import json
import sys
import os
import traceback

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api.gitlab_client import get_gitlab_client
    from api.utils import json_response, error_response, cors_response, parse_request
except ImportError:
    from gitlab_client import get_gitlab_client
    from utils import json_response, error_response, cors_response, parse_request


def handler(request):
    """Handle pipelines API requests."""
    req = parse_request(request)
    
    # Handle CORS preflight
    if req["method"] == "OPTIONS":
        return cors_response()
    
    try:
        client = get_gitlab_client()
        
        if req["method"] == "GET":
            params = req["args"]
            project_id = params.get("project_id")
            
            if not project_id:
                return error_response("project_id parameter is required", 400)
            
            project = client.projects.get(project_id)
            status = params.get("status")
            limit = int(params.get("limit", 20))
            
            list_params = {}
            if status:
                list_params["status"] = status
            
            pipelines = project.pipelines.list(**list_params, get_all=False)
            pipelines = pipelines[:limit]
            
            result = [
                {
                    "id": pipeline.id,
                    "status": pipeline.status,
                    "ref": pipeline.ref,
                    "sha": pipeline.sha,
                    "web_url": pipeline.web_url,
                    "created_at": pipeline.created_at,
                    "updated_at": pipeline.updated_at,
                }
                for pipeline in pipelines
            ]
            return json_response(result)
        
        else:
            return error_response("Method not allowed", 405)
    
    except Exception as e:
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        return error_response(f"{error_msg}\n\nTraceback:\n{traceback_str}", 500)

