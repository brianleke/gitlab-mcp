"""
API endpoint for GitLab issues.
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
    """Handle issues API requests."""
    req = parse_request(request)
    
    # Handle CORS preflight
    if req["method"] == "OPTIONS":
        return cors_response()
    
    try:
        client = get_gitlab_client()
        
        if req["method"] == "GET":
            params = req["args"]
            project_id = params.get("project_id")
            issue_iid = params.get("issue_iid")
            
            if not project_id:
                return error_response("project_id parameter is required", 400)
            
            project = client.projects.get(project_id)
            
            if issue_iid:
                # Get specific issue
                issue = project.issues.get(int(issue_iid))
                result = {
                    "iid": issue.iid,
                    "title": issue.title,
                    "description": issue.description,
                    "state": issue.state,
                    "labels": issue.labels,
                    "author": {
                        "username": issue.author["username"],
                        "name": issue.author["name"],
                    },
                    "assignees": [
                        {
                            "username": a["username"],
                            "name": a["name"],
                        }
                        for a in issue.assignees
                    ],
                    "created_at": issue.created_at,
                    "updated_at": issue.updated_at,
                    "web_url": issue.web_url,
                }
                return json_response(result)
            else:
                # List issues
                state = params.get("state", "opened")
                labels = params.get("labels")
                limit = int(params.get("limit", 20))
                
                list_params = {"state": state}
                if labels:
                    list_params["labels"] = labels.split(",")
                
                issues = project.issues.list(**list_params, get_all=False)
                issues = issues[:limit]
                
                result = [
                    {
                        "iid": issue.iid,
                        "title": issue.title,
                        "description": issue.description,
                        "state": issue.state,
                        "labels": issue.labels,
                        "author": {
                            "username": issue.author["username"],
                            "name": issue.author["name"],
                        },
                        "created_at": issue.created_at,
                        "updated_at": issue.updated_at,
                        "web_url": issue.web_url,
                    }
                    for issue in issues
                ]
                return json_response(result)
        
        elif req["method"] == "POST":
            # Create issue
            body = req["body"]
            project_id = body.get("project_id") or req["args"].get("project_id")
            title = body.get("title")
            
            if not project_id:
                return error_response("project_id is required", 400)
            if not title:
                return error_response("title is required", 400)
            
            project = client.projects.get(project_id)
            issue_data = {
                "title": title,
                "description": body.get("description", ""),
            }
            if body.get("labels"):
                issue_data["labels"] = body["labels"].split(",") if isinstance(body["labels"], str) else body["labels"]
            
            issue = project.issues.create(issue_data)
            
            result = {
                "iid": issue.iid,
                "title": issue.title,
                "state": issue.state,
                "web_url": issue.web_url,
                "message": "Issue created successfully"
            }
            return json_response(result, 201)
        
        else:
            return error_response("Method not allowed", 405)
    
    except Exception as e:
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        return error_response(f"{error_msg}\n\nTraceback:\n{traceback_str}", 500)

