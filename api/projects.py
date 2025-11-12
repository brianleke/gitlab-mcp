"""
API endpoint for GitLab projects.
"""

import sys
import os
import traceback
from http.server import BaseHTTPRequestHandler

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api.gitlab_client import get_gitlab_client
    from api.utils import send_response, parse_query_string
except ImportError:
    from gitlab_client import get_gitlab_client
    from utils import send_response, parse_query_string


class handler(BaseHTTPRequestHandler):
    """Handle projects API requests."""
    
    def do_GET(self):
        try:
            client = get_gitlab_client()
            params = parse_query_string(self.path)
            
            owned = params.get("owned", "false").lower() == "true"
            starred = params.get("starred", "false").lower() == "true"
            search = params.get("search")
            limit = int(params.get("limit", 20))
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
                send_response(self, 200, result)
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
                send_response(self, 200, result)
        except Exception as e:
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            send_response(self, 500, {"error": f"{error_msg}\n\nTraceback:\n{traceback_str}"})
    
    def do_OPTIONS(self):
        send_response(self, 200, {}, cors=True)
    
    def log_message(self, format, *args):
        pass
