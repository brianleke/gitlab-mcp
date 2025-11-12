"""
API endpoint for GitLab pipelines.
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
    """Handle pipelines API requests."""
    
    def do_GET(self):
        try:
            client = get_gitlab_client()
            params = parse_query_string(self.path)
            project_id = params.get("project_id")
            
            if not project_id:
                send_response(self, 400, {"error": "project_id parameter is required"})
                return
            
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
            send_response(self, 200, result)
        except Exception as e:
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            send_response(self, 500, {"error": f"{error_msg}\n\nTraceback:\n{traceback_str}"})
    
    def do_OPTIONS(self):
        send_response(self, 200, {}, cors=True)
    
    def log_message(self, format, *args):
        pass
