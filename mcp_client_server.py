#!/usr/bin/env python3
"""
MCP Server that exposes GitLab REST API endpoints as tools.
This server calls the Vercel-deployed REST API.
"""

import os
import sys
import json
import requests
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize the MCP server
app = Server("gitlab-api-mcp-server")

# API configuration
API_BASE_URL = os.getenv("GITLAB_API_URL", "https://your-project.vercel.app/api")
API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", os.getenv("GITLAB_TOKEN"))


def make_api_request(endpoint: str, method: str = "GET", params: dict = None, body: dict = None) -> dict:
    """Make a request to the GitLab REST API."""
    url = f"{API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {
        "Content-Type": "application/json",
    }
    
    # Add bearer token if available
    if API_BEARER_TOKEN:
        headers["Authorization"] = f"Bearer {API_BEARER_TOKEN}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, params=params, json=body, timeout=30)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from API"}


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available GitLab API tools."""
    return [
        Tool(
            name="get_user_info",
            description="Get information about the current authenticated GitLab user",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="list_projects",
            description="List GitLab projects. Can filter by owned, starred, or search query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "owned": {
                        "type": "boolean",
                        "description": "Only return projects owned by the current user",
                        "default": False
                    },
                    "starred": {
                        "type": "boolean",
                        "description": "Only return starred projects",
                        "default": False
                    },
                    "search": {
                        "type": "string",
                        "description": "Search for projects by name"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of projects to return",
                        "default": 20
                    }
                }
            }
        ),
        Tool(
            name="get_project",
            description="Get detailed information about a specific GitLab project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID or path (e.g., 'group/project' or numeric ID)"
                    }
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="list_issues",
            description="List issues from a GitLab project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID or path"
                    },
                    "state": {
                        "type": "string",
                        "enum": ["opened", "closed", "all"],
                        "description": "Filter by issue state",
                        "default": "opened"
                    },
                    "labels": {
                        "type": "string",
                        "description": "Comma-separated list of label names"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of issues to return",
                        "default": 20
                    }
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="get_issue",
            description="Get detailed information about a specific issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID or path"
                    },
                    "issue_iid": {
                        "type": "integer",
                        "description": "Issue IID (internal ID within the project)"
                    }
                },
                "required": ["project_id", "issue_iid"]
            }
        ),
        Tool(
            name="create_issue",
            description="Create a new issue in a GitLab project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID or path"
                    },
                    "title": {
                        "type": "string",
                        "description": "Issue title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Issue description"
                    },
                    "labels": {
                        "type": "string",
                        "description": "Comma-separated list of labels"
                    }
                },
                "required": ["project_id", "title"]
            }
        ),
        Tool(
            name="list_merge_requests",
            description="List merge requests from a GitLab project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID or path"
                    },
                    "state": {
                        "type": "string",
                        "enum": ["opened", "closed", "merged", "all"],
                        "description": "Filter by MR state",
                        "default": "opened"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of MRs to return",
                        "default": 20
                    }
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="get_merge_request",
            description="Get detailed information about a specific merge request",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID or path"
                    },
                    "mr_iid": {
                        "type": "integer",
                        "description": "Merge request IID"
                    }
                },
                "required": ["project_id", "mr_iid"]
            }
        ),
        Tool(
            name="list_pipelines",
            description="List CI/CD pipelines for a GitLab project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID or path"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["running", "pending", "success", "failed", "canceled", "skipped"],
                        "description": "Filter by pipeline status"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of pipelines to return",
                        "default": 20
                    }
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="list_groups",
            description="List GitLab groups",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search for groups by name"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of groups to return",
                        "default": 20
                    }
                }
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls by making requests to the REST API."""
    try:
        result = None
        
        if name == "get_user_info":
            result = make_api_request("user")
        
        elif name == "list_projects":
            params = {}
            if arguments.get("owned"):
                params["owned"] = "true"
            if arguments.get("starred"):
                params["starred"] = "true"
            if arguments.get("search"):
                params["search"] = arguments["search"]
            if arguments.get("limit"):
                params["limit"] = str(arguments["limit"])
            result = make_api_request("projects", params=params)
        
        elif name == "get_project":
            project_id = arguments.get("project_id")
            if not project_id:
                result = {"error": "project_id is required"}
            else:
                result = make_api_request("projects", params={"id": project_id})
        
        elif name == "list_issues":
            project_id = arguments.get("project_id")
            if not project_id:
                result = {"error": "project_id is required"}
            else:
                params = {"project_id": project_id}
                if arguments.get("state"):
                    params["state"] = arguments["state"]
                if arguments.get("labels"):
                    params["labels"] = arguments["labels"]
                if arguments.get("limit"):
                    params["limit"] = str(arguments["limit"])
                result = make_api_request("issues", params=params)
        
        elif name == "get_issue":
            project_id = arguments.get("project_id")
            issue_iid = arguments.get("issue_iid")
            if not project_id or not issue_iid:
                result = {"error": "project_id and issue_iid are required"}
            else:
                params = {
                    "project_id": project_id,
                    "issue_iid": str(issue_iid)
                }
                result = make_api_request("issues", params=params)
        
        elif name == "create_issue":
            project_id = arguments.get("project_id")
            title = arguments.get("title")
            if not project_id or not title:
                result = {"error": "project_id and title are required"}
            else:
                body = {
                    "project_id": project_id,
                    "title": title,
                    "description": arguments.get("description", ""),
                }
                if arguments.get("labels"):
                    body["labels"] = arguments["labels"]
                result = make_api_request("issues", method="POST", body=body)
        
        elif name == "list_merge_requests":
            project_id = arguments.get("project_id")
            if not project_id:
                result = {"error": "project_id is required"}
            else:
                params = {"project_id": project_id}
                if arguments.get("state"):
                    params["state"] = arguments["state"]
                if arguments.get("limit"):
                    params["limit"] = str(arguments["limit"])
                result = make_api_request("merge_requests", params=params)
        
        elif name == "get_merge_request":
            project_id = arguments.get("project_id")
            mr_iid = arguments.get("mr_iid")
            if not project_id or not mr_iid:
                result = {"error": "project_id and mr_iid are required"}
            else:
                params = {
                    "project_id": project_id,
                    "mr_iid": str(mr_iid)
                }
                result = make_api_request("merge_requests", params=params)
        
        elif name == "list_pipelines":
            project_id = arguments.get("project_id")
            if not project_id:
                result = {"error": "project_id is required"}
            else:
                params = {"project_id": project_id}
                if arguments.get("status"):
                    params["status"] = arguments["status"]
                if arguments.get("limit"):
                    params["limit"] = str(arguments["limit"])
                result = make_api_request("pipelines", params=params)
        
        elif name == "list_groups":
            params = {}
            if arguments.get("search"):
                params["search"] = arguments["search"]
            if arguments.get("limit"):
                params["limit"] = str(arguments["limit"])
            result = make_api_request("groups", params=params)
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        if result is None:
            result = {"error": "Tool execution failed"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

