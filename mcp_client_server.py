#!/usr/bin/env python3
"""
MCP Server that exposes GitLab REST API endpoints as tools.
This server automatically discovers tools from the API documentation.
"""

import os
import sys
import json
import requests
from typing import Any, Optional, Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize the MCP server
app = Server("gitlab-api-mcp-server")

# API configuration
API_BASE_URL = os.getenv("GITLAB_API_URL", "https://your-project.vercel.app/api")
API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", os.getenv("GITLAB_TOKEN"))

# Cache for discovered tools
_discovered_tools: Optional[List[Tool]] = None
_api_docs: Optional[Dict] = None


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


def discover_api_documentation() -> Dict:
    """Fetch and cache API documentation from the /api/ endpoint."""
    global _api_docs
    
    if _api_docs is not None:
        return _api_docs
    
    try:
        # The /api/ endpoint doesn't require auth, but we'll try with token if available
        docs = make_api_request("")
        if "endpoints" in docs:
            _api_docs = docs
            return docs
        else:
            # If we got an error, try without auth for the docs endpoint
            url = f"{API_BASE_URL.rstrip('/')}/"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                _api_docs = response.json()
                return _api_docs
    except Exception as e:
        print(f"Warning: Could not fetch API docs: {e}", file=sys.stderr)
    
    # Return empty docs if discovery fails
    _api_docs = {"endpoints": {}}
    return _api_docs


def convert_endpoint_to_tool(endpoint_path: str, endpoint_info: Dict) -> Optional[Tool]:
    """Convert an API endpoint definition to an MCP Tool."""
    method = endpoint_info.get("method", "GET")
    description = endpoint_info.get("description", f"Call {endpoint_path}")
    query_params = endpoint_info.get("query_params", {})
    body_params = endpoint_info.get("body", {})
    
    # Build input schema
    properties = {}
    required = []
    
    # Add query parameters
    for param_name, param_desc in query_params.items():
        param_type = "string"
        if "required" in param_desc.lower() or param_name in ["project_id", "id"]:
            required.append(param_name)
        
        # Infer type from description
        if "limit" in param_name or "iid" in param_name or "id" in param_name:
            param_type = "integer"
        elif "true/false" in param_desc.lower() or param_name in ["owned", "starred"]:
            param_type = "boolean"
        elif "enum" in param_desc.lower() or "state" in param_name or "status" in param_name:
            # Extract enum values if possible
            if "opened/closed" in param_desc.lower():
                param_type = {"type": "string", "enum": ["opened", "closed", "all"]}
            elif "running/pending" in param_desc.lower():
                param_type = {"type": "string", "enum": ["running", "pending", "success", "failed", "canceled", "skipped"]}
            else:
                param_type = "string"
        
        if isinstance(param_type, dict):
            properties[param_name] = {
                "type": param_type["type"],
                "enum": param_type.get("enum", []),
                "description": param_desc
            }
        else:
            properties[param_name] = {
                "type": param_type,
                "description": param_desc
            }
    
    # Add body parameters for POST requests
    if method == "POST" and body_params:
        for param_name, param_desc in body_params.items():
            param_type = "string"
            if "required" in param_desc.lower() or param_name in ["project_id", "title"]:
                required.append(param_name)
            
            properties[param_name] = {
                "type": param_type,
                "description": param_desc
            }
    
    # Create tool name from endpoint path
    tool_name = endpoint_path.replace("/api/", "").replace("/", "_").replace("-", "_")
    if not tool_name:
        tool_name = "api_index"
    
    # Handle duplicate names (e.g., /api/issues with GET and POST)
    if method == "POST":
        tool_name = f"create_{tool_name}" if not tool_name.startswith("create_") else tool_name
    elif "get" not in tool_name.lower() and method == "GET":
        # For GET with specific ID, add "get_" prefix
        if any(param in required for param in ["id", "issue_iid", "mr_iid"]):
            tool_name = f"get_{tool_name}"
    
    return Tool(
        name=tool_name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": properties,
            "required": required if required else None
        }
    )


def discover_tools() -> List[Tool]:
    """Discover tools from the API documentation."""
    global _discovered_tools
    
    if _discovered_tools is not None:
        return _discovered_tools
    
    docs = discover_api_documentation()
    tools = []
    seen_tool_names = set()
    
    endpoints = docs.get("endpoints", {})
    
    # Group endpoints by path (since same path can have multiple methods)
    endpoint_groups = {}
    for endpoint_path, endpoint_info in endpoints.items():
        # Normalize path (remove /api/ prefix)
        normalized_path = endpoint_path.replace("/api/", "").strip("/")
        if normalized_path not in endpoint_groups:
            endpoint_groups[normalized_path] = []
        
        if isinstance(endpoint_info, dict):
            endpoint_groups[normalized_path].append(endpoint_info)
        elif isinstance(endpoint_info, list):
            endpoint_groups[normalized_path].extend(endpoint_info)
    
    # Process each endpoint group
    for endpoint_path, methods in endpoint_groups.items():
        for method_info in methods:
            if isinstance(method_info, dict) and "method" in method_info:
                # Reconstruct full path for tool conversion
                full_path = f"/api/{endpoint_path}" if endpoint_path else "/api/"
                tool = convert_endpoint_to_tool(full_path, method_info)
                if tool and tool.name not in seen_tool_names:
                    tools.append(tool)
                    seen_tool_names.add(tool.name)
    
    # If no tools discovered, fall back to hardcoded tools
    if not tools:
        tools = get_fallback_tools()
    
    _discovered_tools = tools
    return tools


def get_fallback_tools() -> List[Tool]:
    """Fallback tools if API discovery fails."""
    return [
        Tool(
            name="get_user_info",
            description="Get information about the current authenticated GitLab user",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="list_projects",
            description="List GitLab projects",
            inputSchema={
                "type": "object",
                "properties": {
                    "owned": {"type": "boolean", "description": "Filter to owned projects"},
                    "starred": {"type": "boolean", "description": "Filter to starred projects"},
                    "search": {"type": "string", "description": "Search projects by name"},
                    "limit": {"type": "integer", "description": "Maximum number of results", "default": 20}
                }
            }
        ),
    ]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available GitLab API tools (auto-discovered from API documentation)."""
    return discover_tools()


def route_tool_to_endpoint(tool_name: str, arguments: dict) -> tuple[str, str, dict, dict]:
    """Route a tool name to the appropriate API endpoint and method."""
    # Use the discovered tools to find the correct endpoint
    tools = discover_tools()
    
    # Find the tool by name
    tool_info = None
    for tool in tools:
        if tool.name == tool_name:
            # We need to map back to the endpoint
            # Extract from tool name or use cached mapping
            break
    
    # Extract endpoint from tool name (fallback if discovery didn't work)
    endpoint = tool_name.replace("create_", "").replace("get_", "").replace("list_", "").replace("api_", "")
    
    # Map common patterns
    endpoint_map = {
        "user": "user",
        "projects": "projects",
        "project": "projects",
        "issues": "issues",
        "issue": "issues",
        "merge_requests": "merge_requests",
        "merge_request": "merge_requests",
        "pipelines": "pipelines",
        "pipeline": "pipelines",
        "groups": "groups",
        "group": "groups",
        "index": "",  # Root endpoint
    }
    
    # Determine endpoint
    api_endpoint = endpoint_map.get(endpoint, endpoint)
    
    # Determine method from tool name
    method = "POST" if tool_name.startswith("create_") else "GET"
    
    # Build params and body
    params = {}
    body = {}
    
    # Convert arguments to params/body
    for key, value in arguments.items():
        if method == "POST" and key in ["project_id", "title", "description", "labels"]:
            body[key] = value
        else:
            # Convert boolean to string for query params
            if isinstance(value, bool):
                params[key] = "true" if value else "false"
            else:
                params[key] = str(value) if value is not None else None
    
    # Handle special cases
    if tool_name.startswith("get_") and "id" in arguments:
        params["id"] = arguments.get("id") or arguments.get("project_id")
    elif tool_name.startswith("get_") and "issue_iid" in arguments:
        params["issue_iid"] = str(arguments["issue_iid"])
    elif tool_name.startswith("get_") and "mr_iid" in arguments:
        params["mr_iid"] = str(arguments["mr_iid"])
    
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    
    return api_endpoint, method, params, body


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls by making requests to the REST API."""
    try:
        # Route tool to endpoint
        endpoint, method, params, body = route_tool_to_endpoint(name, arguments)
        
        # Make API request
        result = make_api_request(endpoint, method=method, params=params, body=body)
        
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

