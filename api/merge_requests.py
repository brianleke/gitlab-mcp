"""
API endpoint for GitLab merge requests.
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
    """Handle merge requests API requests."""
    req = parse_request(request)
    
    # Handle CORS preflight
    if req["method"] == "OPTIONS":
        return cors_response()
    
    try:
        client = get_gitlab_client()
        
        if req["method"] == "GET":
            params = req["args"]
            project_id = params.get("project_id")
            mr_iid = params.get("mr_iid")
            
            if not project_id:
                return error_response("project_id parameter is required", 400)
            
            project = client.projects.get(project_id)
            
            if mr_iid:
                # Get specific merge request
                mr = project.mergerequests.get(int(mr_iid))
                result = {
                    "iid": mr.iid,
                    "title": mr.title,
                    "description": mr.description,
                    "state": mr.state,
                    "source_branch": mr.source_branch,
                    "target_branch": mr.target_branch,
                    "author": {
                        "username": mr.author["username"],
                        "name": mr.author["name"],
                    },
                    "assignees": [
                        {
                            "username": a["username"],
                            "name": a["name"],
                        }
                        for a in mr.assignees
                    ],
                    "created_at": mr.created_at,
                    "updated_at": mr.updated_at,
                    "web_url": mr.web_url,
                }
                return json_response(result)
            else:
                # List merge requests
                state = params.get("state", "opened")
                limit = int(params.get("limit", 20))
                
                mrs = project.mergerequests.list(state=state, get_all=False)
                mrs = mrs[:limit]
                
                result = [
                    {
                        "iid": mr.iid,
                        "title": mr.title,
                        "state": mr.state,
                        "source_branch": mr.source_branch,
                        "target_branch": mr.target_branch,
                        "author": {
                            "username": mr.author["username"],
                            "name": mr.author["name"],
                        },
                        "created_at": mr.created_at,
                        "updated_at": mr.updated_at,
                        "web_url": mr.web_url,
                    }
                    for mr in mrs
                ]
                return json_response(result)
        
        else:
            return error_response("Method not allowed", 405)
    
    except Exception as e:
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        return error_response(f"{error_msg}\n\nTraceback:\n{traceback_str}", 500)

