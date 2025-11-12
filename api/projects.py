"""
API endpoint for GitLab projects.
"""

import json
from gitlab_client import get_gitlab_client
from utils import json_response, error_response, cors_response, parse_request


def handler(request):
    """Handle projects API requests."""
    req = parse_request(request)
    
    # Handle CORS preflight
    if req["method"] == "OPTIONS":
        return cors_response()
    
    try:
        client = get_gitlab_client()
        
        if req["method"] == "GET":
            # Parse query parameters
            params = req["args"]
            owned = params.get("owned", "false").lower() == "true"
            starred = params.get("starred", "false").lower() == "true"
            search = params.get("search")
            limit = int(params.get("limit", 20))
            
            # Get project ID from path if present
            project_id = params.get("id")
            
            if project_id:
                # Get specific project
                project = client.projects.get(project_id)
                result = {
                    "id": project.id,
                    "name": project.name,
                    "path": project.path,
                    "path_with_namespace": project.path_with_namespace,
                    "web_url": project.web_url,
                    "description": project.description,
                    "visibility": project.visibility,
                    "default_branch": project.default_branch,
                    "ssh_url_to_repo": project.ssh_url_to_repo,
                    "http_url_to_repo": project.http_url_to_repo,
                    "created_at": project.created_at,
                    "last_activity_at": project.last_activity_at,
                    "star_count": project.star_count,
                    "forks_count": project.forks_count,
                }
                return json_response(result)
            else:
                # List projects
                list_params = {}
                if owned:
                    list_params["owned"] = True
                if starred:
                    list_params["starred"] = True
                if search:
                    list_params["search"] = search
                
                projects = client.projects.list(**list_params, get_all=False)
                projects = projects[:limit]
                
                result = [
                    {
                        "id": p.id,
                        "name": p.name,
                        "path_with_namespace": p.path_with_namespace,
                        "web_url": p.web_url,
                        "description": p.description,
                        "visibility": p.visibility,
                        "default_branch": p.default_branch,
                    }
                    for p in projects
                ]
                return json_response(result)
        
        else:
            return error_response("Method not allowed", 405)
    
    except Exception as e:
        return error_response(str(e), 500)

