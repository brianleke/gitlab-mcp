#!/usr/bin/env python3
"""
GitLab MCP Server
A Model Context Protocol server for integrating with GitLab.
"""

import os
import sys
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import gitlab
import json
from datetime import datetime

# Initialize the MCP server
app = Server("gitlab-mcp-server")

# GitLab client instance (will be initialized on startup)
gl: Optional[gitlab.Gitlab] = None


def get_gitlab_client() -> gitlab.Gitlab:
    """Get or create the GitLab client instance."""
    global gl
    if gl is None:
        gitlab_url = os.getenv("GITLAB_URL", "https://gitlab.com")
        gitlab_token = os.getenv("GITLAB_TOKEN")
        
        if not gitlab_token:
            raise ValueError(
                "GITLAB_TOKEN environment variable is required. "
                "Get a personal access token from GitLab with 'api' scope."
            )
        
        gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
        gl.auth()
    
    return gl


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available GitLab resources."""
    try:
        client = get_gitlab_client()
        user = client.user
        
        return [
            Resource(
                uri="gitlab://user",
                name="Current User",
                description=f"GitLab user: {user.username}",
                mimeType="application/json"
            ),
            Resource(
                uri="gitlab://projects",
                name="All Projects",
                description="List of all accessible GitLab projects",
                mimeType="application/json"
            ),
            Resource(
                uri="gitlab://groups",
                name="All Groups",
                description="List of all accessible GitLab groups",
                mimeType="application/json"
            ),
        ]
    except Exception as e:
        return [
            Resource(
                uri="gitlab://error",
                name="Error",
                description=f"Error connecting to GitLab: {str(e)}",
                mimeType="text/plain"
            )
        ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read a GitLab resource."""
    try:
        client = get_gitlab_client()
        
        if uri == "gitlab://user":
            user = client.user
            return json.dumps({
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "email": user.email,
                "avatar_url": user.avatar_url,
            }, indent=2)
        
        elif uri == "gitlab://projects":
            projects = client.projects.list(owned=True, get_all=True)
            return json.dumps([
                {
                    "id": p.id,
                    "name": p.name,
                    "path": p.path,
                    "path_with_namespace": p.path_with_namespace,
                    "web_url": p.web_url,
                    "description": p.description,
                    "visibility": p.visibility,
                    "default_branch": p.default_branch,
                    "last_activity_at": p.last_activity_at,
                }
                for p in projects[:100]  # Limit to 100 for performance
            ], indent=2)
        
        elif uri == "gitlab://groups":
            groups = client.groups.list(get_all=True)
            return json.dumps([
                {
                    "id": g.id,
                    "name": g.name,
                    "path": g.path,
                    "full_path": g.full_path,
                    "web_url": g.web_url,
                    "description": g.description,
                }
                for g in groups[:100]  # Limit to 100 for performance
            ], indent=2)
        
        else:
            return f"Unknown resource: {uri}"
    
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available GitLab tools."""
    return [
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
        Tool(
            name="get_user_info",
            description="Get information about the current authenticated user",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        client = get_gitlab_client()
        
        if name == "list_projects":
            owned = arguments.get("owned", False)
            starred = arguments.get("starred", False)
            search = arguments.get("search")
            limit = arguments.get("limit", 20)
            
            params = {}
            if owned:
                params["owned"] = True
            if starred:
                params["starred"] = True
            if search:
                params["search"] = search
            
            projects = client.projects.list(**params, get_all=False)
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
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_project":
            project_id = arguments["project_id"]
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
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "list_issues":
            project_id = arguments["project_id"]
            state = arguments.get("state", "opened")
            labels = arguments.get("labels")
            limit = arguments.get("limit", 20)
            
            project = client.projects.get(project_id)
            params = {"state": state}
            if labels:
                params["labels"] = labels.split(",")
            
            issues = project.issues.list(**params, get_all=False)
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
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_issue":
            project_id = arguments["project_id"]
            issue_iid = arguments["issue_iid"]
            
            project = client.projects.get(project_id)
            issue = project.issues.get(issue_iid)
            
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
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "create_issue":
            project_id = arguments["project_id"]
            title = arguments["title"]
            description = arguments.get("description", "")
            labels = arguments.get("labels", "")
            
            project = client.projects.get(project_id)
            issue_data = {"title": title, "description": description}
            if labels:
                issue_data["labels"] = labels.split(",")
            
            issue = project.issues.create(issue_data)
            
            result = {
                "iid": issue.iid,
                "title": issue.title,
                "state": issue.state,
                "web_url": issue.web_url,
                "message": "Issue created successfully"
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "list_merge_requests":
            project_id = arguments["project_id"]
            state = arguments.get("state", "opened")
            limit = arguments.get("limit", 20)
            
            project = client.projects.get(project_id)
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
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_merge_request":
            project_id = arguments["project_id"]
            mr_iid = arguments["mr_iid"]
            
            project = client.projects.get(project_id)
            mr = project.mergerequests.get(mr_iid)
            
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
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "list_pipelines":
            project_id = arguments["project_id"]
            status = arguments.get("status")
            limit = arguments.get("limit", 20)
            
            project = client.projects.get(project_id)
            params = {}
            if status:
                params["status"] = status
            
            pipelines = project.pipelines.list(**params, get_all=False)
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
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "list_groups":
            search = arguments.get("search")
            limit = arguments.get("limit", 20)
            
            params = {}
            if search:
                params["search"] = search
            
            groups = client.groups.list(**params, get_all=False)
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
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_user_info":
            user = client.user
            
            result = {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "web_url": user.web_url,
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2)
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

