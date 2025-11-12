"""
API endpoint for GitLab groups.
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
    """Handle groups API requests."""
    
    def do_GET(self):
        try:
            # Check authentication
            is_auth, auth_error = require_auth(self)
            if not is_auth:
                send_response(self, 401, {"error": auth_error})
                return
            
            client = get_gitlab_client()
            params = parse_query_string(self.path)
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
            send_response(self, 200, result)
        except Exception as e:
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            send_response(self, 500, {"error": f"{error_msg}\n\nTraceback:\n{traceback_str}"})
    
    def do_OPTIONS(self):
        send_response(self, 200, {}, cors=True)
    
    def log_message(self, format, *args):
        pass
