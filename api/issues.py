"""
API endpoint for GitLab issues.
"""

import sys
import os
import traceback
from http.server import BaseHTTPRequestHandler

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api.gitlab_client import get_gitlab_client
    from api.utils import send_response, parse_query_string, read_request_body, require_auth
except ImportError:
    from gitlab_client import get_gitlab_client
    from utils import send_response, parse_query_string, read_request_body, require_auth


class handler(BaseHTTPRequestHandler):
    """Handle issues API requests."""
    
    def do_GET(self):
        try:
            # Check authentication
            is_auth, auth_error = require_auth(self)
            if not is_auth:
                send_response(self, 401, {"error": auth_error})
                return
            
            client = get_gitlab_client()
            params = parse_query_string(self.path)
            project_id = params.get("project_id")
            issue_iid = params.get("issue_iid")
            
            if not project_id:
                send_response(self, 400, {"error": "project_id parameter is required"})
                return
            
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
                send_response(self, 200, result)
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
                send_response(self, 200, result)
        except Exception as e:
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            send_response(self, 500, {"error": f"{error_msg}\n\nTraceback:\n{traceback_str}"})
    
    def do_POST(self):
        try:
            # Check authentication
            is_auth, auth_error = require_auth(self)
            if not is_auth:
                send_response(self, 401, {"error": auth_error})
                return
            
            client = get_gitlab_client()
            body = read_request_body(self)
            params = parse_query_string(self.path)
            
            project_id = body.get("project_id") or params.get("project_id")
            title = body.get("title")
            
            if not project_id:
                send_response(self, 400, {"error": "project_id is required"})
                return
            if not title:
                send_response(self, 400, {"error": "title is required"})
                return
            
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
            send_response(self, 201, result)
        except Exception as e:
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            send_response(self, 500, {"error": f"{error_msg}\n\nTraceback:\n{traceback_str}"})
    
    def do_OPTIONS(self):
        send_response(self, 200, {}, cors=True)
    
    def log_message(self, format, *args):
        pass
