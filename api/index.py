"""
Main API index endpoint - provides API documentation.
"""

import sys
import os
import json
import traceback
from http.server import BaseHTTPRequestHandler

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api.utils import send_response, require_auth
except ImportError:
    from utils import send_response, require_auth


class handler(BaseHTTPRequestHandler):
    """Handle index API requests."""
    
    def do_GET(self):
        try:
            # Index endpoint is public (documentation only)
            docs = {
                "name": "GitLab MCP API",
                "version": "1.0.0",
                "description": "REST API for GitLab integration via Model Context Protocol",
                "endpoints": {
                    "/api/user": {
                        "method": "GET",
                        "description": "Get current authenticated user information"
                    },
                    "/api/projects": {
                        "method": "GET",
                        "description": "List or get GitLab projects",
                        "query_params": {
                            "id": "Get specific project by ID or path",
                            "owned": "Filter to owned projects (true/false)",
                            "starred": "Filter to starred projects (true/false)",
                            "search": "Search projects by name",
                            "limit": "Maximum number of results (default: 20)"
                        }
                    },
                    "/api/issues": {
                        "method": "GET",
                        "description": "List or get GitLab issues",
                        "query_params": {
                            "project_id": "Project ID or path (required)",
                            "issue_iid": "Get specific issue by IID",
                            "state": "Filter by state (opened/closed/all)",
                            "labels": "Comma-separated list of labels",
                            "limit": "Maximum number of results (default: 20)"
                        }
                    },
                    "/api/issues": {
                        "method": "POST",
                        "description": "Create a new issue",
                        "body": {
                            "project_id": "Project ID or path (required)",
                            "title": "Issue title (required)",
                            "description": "Issue description",
                            "labels": "Comma-separated list of labels"
                        }
                    },
                    "/api/merge_requests": {
                        "method": "GET",
                        "description": "List or get merge requests",
                        "query_params": {
                            "project_id": "Project ID or path (required)",
                            "mr_iid": "Get specific MR by IID",
                            "state": "Filter by state (opened/closed/merged/all)",
                            "limit": "Maximum number of results (default: 20)"
                        }
                    },
                    "/api/pipelines": {
                        "method": "GET",
                        "description": "List CI/CD pipelines",
                        "query_params": {
                            "project_id": "Project ID or path (required)",
                            "status": "Filter by status (running/pending/success/failed/canceled/skipped)",
                            "limit": "Maximum number of results (default: 20)"
                        }
                    },
                    "/api/groups": {
                        "method": "GET",
                        "description": "List GitLab groups",
                        "query_params": {
                            "search": "Search groups by name",
                            "limit": "Maximum number of results (default: 20)"
                        }
                    }
                },
                "authentication": {
                    "type": "Bearer Token",
                    "header": "Authorization: Bearer <token>",
                    "note": "All endpoints require a Bearer token in the Authorization header. Configure tokens via API_BEARER_TOKENS environment variable (or GITLAB_TOKEN as fallback)."
                }
            }
            send_response(self, 200, docs)
        except Exception as e:
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            send_response(self, 500, {"error": f"{error_msg}\n\nTraceback:\n{traceback_str}"})
    
    def do_OPTIONS(self):
        send_response(self, 200, {}, cors=True)
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

