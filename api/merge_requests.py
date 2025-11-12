"""
API endpoint for GitLab merge requests.
"""

import sys
import os
import traceback
from http.server import BaseHTTPRequestHandler

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api.gitlab_client import get_gitlab_client
    from api.utils import send_response, parse_query_string, require_auth
except ImportError:
    from gitlab_client import get_gitlab_client
    from utils import send_response, parse_query_string, require_auth


class handler(BaseHTTPRequestHandler):
    """Handle merge requests API requests."""
    
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
            mr_iid = params.get("mr_iid")
            
            if not project_id:
                send_response(self, 400, {"error": "project_id parameter is required"})
                return
            
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
                send_response(self, 200, result)
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
                send_response(self, 200, result)
        except Exception as e:
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            send_response(self, 500, {"error": f"{error_msg}\n\nTraceback:\n{traceback_str}"})
    
    def do_OPTIONS(self):
        send_response(self, 200, {}, cors=True)
    
    def log_message(self, format, *args):
        pass
