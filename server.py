"""
GitLab MCP Server using FastMCP
Exposes GitLab API endpoints as MCP tools
"""

import os
import httpx
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("GitLab MCP Server")

# GitLab API base URL - can be customized via environment variable
GITLAB_BASE_URL = os.getenv("GITLAB_BASE_URL", "https://gitlab.com/api/v4")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN", "")

# Server bearer token for authorization (optional but recommended)
SERVER_BEARER_TOKEN = os.getenv("SERVER_BEARER_TOKEN", "")

# Create HTTP client for GitLab API
client = httpx.AsyncClient(
    base_url=GITLAB_BASE_URL,
    headers={
        "Authorization": f"Bearer {GITLAB_TOKEN}",
        "Content-Type": "application/json",
    },
    timeout=30.0,
)


def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers for GitLab API"""
    headers = {"Content-Type": "application/json"}
    if GITLAB_TOKEN:
        headers["Authorization"] = f"Bearer {GITLAB_TOKEN}"
    return headers


def verify_bearer_token(authorization_header: Optional[str]) -> bool:
    """
    Verify bearer token authorization
    
    Args:
        authorization_header: Authorization header value (e.g., "Bearer token123")
    
    Returns:
        True if token is valid or no token is required, False otherwise
    """
    # If no server token is configured, allow access (backward compatible)
    if not SERVER_BEARER_TOKEN:
        return True
    
    # If token is configured, require valid bearer token
    if not authorization_header:
        return False
    
    # Extract token from "Bearer <token>" format
    if not authorization_header.startswith("Bearer "):
        return False
    
    token = authorization_header[7:].strip()  # Remove "Bearer " prefix
    return token == SERVER_BEARER_TOKEN


# ==================== PROJECT TOOLS ====================

@mcp.tool()
async def list_projects(
    search: Optional[str] = None,
    owned: bool = False,
    starred: bool = False,
    visibility: Optional[str] = None,
    order_by: str = "created_at",
    sort: str = "desc",
    per_page: int = 20,
    page: int = 1,
) -> Dict[str, Any]:
    """
    List GitLab projects
    
    Args:
        search: Search projects by name
        owned: Return only projects owned by the authenticated user
        starred: Return only starred projects
        visibility: Filter by visibility (public, internal, private)
        order_by: Order by field (id, name, path, created_at, updated_at, last_activity_at)
        sort: Sort order (asc, desc)
        per_page: Number of results per page (max 100)
        page: Page number
    
    Returns:
        List of projects with their details
    """
    params = {
        "order_by": order_by,
        "sort": sort,
        "per_page": min(per_page, 100),
        "page": page,
    }
    
    if search:
        params["search"] = search
    if owned:
        params["owned"] = "true"
    if starred:
        params["starred"] = "true"
    if visibility:
        params["visibility"] = visibility
    
    response = await client.get("/projects", params=params, headers=get_auth_headers())
    response.raise_for_status()
    return {"projects": response.json(), "total": len(response.json())}


@mcp.tool()
async def get_project(project_id: str) -> Dict[str, Any]:
    """
    Get details of a specific GitLab project
    
    Args:
        project_id: Project ID or path (e.g., "namespace/project" or numeric ID)
    
    Returns:
        Project details
    """
    response = await client.get(f"/projects/{project_id}", headers=get_auth_headers())
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def create_project(
    name: str,
    path: Optional[str] = None,
    namespace_id: Optional[int] = None,
    description: Optional[str] = None,
    visibility: str = "private",
    initialize_with_readme: bool = False,
) -> Dict[str, Any]:
    """
    Create a new GitLab project
    
    Args:
        name: Project name
        path: Repository path (defaults to name if not provided)
        namespace_id: Namespace ID for the project
        description: Project description
        visibility: Project visibility (private, internal, public)
        initialize_with_readme: Initialize repository with a README
    
    Returns:
        Created project details
    """
    data = {
        "name": name,
        "visibility": visibility,
        "initialize_with_readme": initialize_with_readme,
    }
    
    if path:
        data["path"] = path
    if namespace_id:
        data["namespace_id"] = namespace_id
    if description:
        data["description"] = description
    
    response = await client.post("/projects", json=data, headers=get_auth_headers())
    response.raise_for_status()
    return response.json()


# ==================== ISSUE TOOLS ====================

@mcp.tool()
async def list_issues(
    project_id: Optional[str] = None,
    state: str = "opened",
    labels: Optional[str] = None,
    search: Optional[str] = None,
    assignee_username: Optional[str] = None,
    author_username: Optional[str] = None,
    per_page: int = 20,
    page: int = 1,
) -> Dict[str, Any]:
    """
    List GitLab issues
    
    Args:
        project_id: Filter by project ID or path (optional, if not provided lists all issues)
        state: Filter by state (opened, closed, all)
        labels: Comma-separated list of label names
        search: Search issues by title and description
        assignee_username: Filter by assignee username
        author_username: Filter by author username
        per_page: Number of results per page (max 100)
        page: Page number
    
    Returns:
        List of issues
    """
    params = {
        "state": state,
        "per_page": min(per_page, 100),
        "page": page,
    }
    
    if labels:
        params["labels"] = labels
    if search:
        params["search"] = search
    if assignee_username:
        params["assignee_username"] = assignee_username
    if author_username:
        params["author_username"] = author_username
    
    endpoint = f"/projects/{project_id}/issues" if project_id else "/issues"
    response = await client.get(endpoint, params=params, headers=get_auth_headers())
    response.raise_for_status()
    return {"issues": response.json(), "total": len(response.json())}


@mcp.tool()
async def get_issue(project_id: str, issue_iid: int) -> Dict[str, Any]:
    """
    Get details of a specific issue
    
    Args:
        project_id: Project ID or path
        issue_iid: Issue IID (internal ID)
    
    Returns:
        Issue details
    """
    response = await client.get(
        f"/projects/{project_id}/issues/{issue_iid}",
        headers=get_auth_headers()
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def create_issue(
    project_id: str,
    title: str,
    description: Optional[str] = None,
    labels: Optional[str] = None,
    assignee_ids: Optional[List[int]] = None,
    milestone_id: Optional[int] = None,
    due_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new issue in a project
    
    Args:
        project_id: Project ID or path
        title: Issue title
        description: Issue description
        labels: Comma-separated list of label names
        assignee_ids: List of user IDs to assign the issue to
        milestone_id: Milestone ID
        due_date: Due date in YYYY-MM-DD format
    
    Returns:
        Created issue details
    """
    data = {"title": title}
    
    if description:
        data["description"] = description
    if labels:
        data["labels"] = labels
    if assignee_ids:
        data["assignee_ids"] = assignee_ids
    if milestone_id:
        data["milestone_id"] = milestone_id
    if due_date:
        data["due_date"] = due_date
    
    response = await client.post(
        f"/projects/{project_id}/issues",
        json=data,
        headers=get_auth_headers()
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def update_issue(
    project_id: str,
    issue_iid: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    state_event: Optional[str] = None,
    labels: Optional[str] = None,
    assignee_ids: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """
    Update an existing issue
    
    Args:
        project_id: Project ID or path
        issue_iid: Issue IID
        title: New title
        description: New description
        state_event: State change (close, reopen)
        labels: Comma-separated list of label names
        assignee_ids: List of user IDs to assign the issue to
    
    Returns:
        Updated issue details
    """
    data = {}
    
    if title:
        data["title"] = title
    if description:
        data["description"] = description
    if state_event:
        data["state_event"] = state_event
    if labels:
        data["labels"] = labels
    if assignee_ids is not None:
        data["assignee_ids"] = assignee_ids
    
    response = await client.put(
        f"/projects/{project_id}/issues/{issue_iid}",
        json=data,
        headers=get_auth_headers()
    )
    response.raise_for_status()
    return response.json()


# ==================== MERGE REQUEST TOOLS ====================

@mcp.tool()
async def list_merge_requests(
    project_id: Optional[str] = None,
    state: str = "opened",
    labels: Optional[str] = None,
    search: Optional[str] = None,
    target_branch: Optional[str] = None,
    source_branch: Optional[str] = None,
    per_page: int = 20,
    page: int = 1,
) -> Dict[str, Any]:
    """
    List GitLab merge requests
    
    Args:
        project_id: Filter by project ID or path (optional)
        state: Filter by state (opened, closed, locked, merged, all)
        labels: Comma-separated list of label names
        search: Search merge requests by title and description
        target_branch: Filter by target branch
        source_branch: Filter by source branch
        per_page: Number of results per page (max 100)
        page: Page number
    
    Returns:
        List of merge requests
    """
    params = {
        "state": state,
        "per_page": min(per_page, 100),
        "page": page,
    }
    
    if labels:
        params["labels"] = labels
    if search:
        params["search"] = search
    if target_branch:
        params["target_branch"] = target_branch
    if source_branch:
        params["source_branch"] = source_branch
    
    endpoint = f"/projects/{project_id}/merge_requests" if project_id else "/merge_requests"
    response = await client.get(endpoint, params=params, headers=get_auth_headers())
    response.raise_for_status()
    return {"merge_requests": response.json(), "total": len(response.json())}


@mcp.tool()
async def get_merge_request(project_id: str, merge_request_iid: int) -> Dict[str, Any]:
    """
    Get details of a specific merge request
    
    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request IID
    
    Returns:
        Merge request details
    """
    response = await client.get(
        f"/projects/{project_id}/merge_requests/{merge_request_iid}",
        headers=get_auth_headers()
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def create_merge_request(
    project_id: str,
    source_branch: str,
    target_branch: str,
    title: str,
    description: Optional[str] = None,
    labels: Optional[str] = None,
    assignee_id: Optional[int] = None,
    remove_source_branch: bool = False,
) -> Dict[str, Any]:
    """
    Create a new merge request
    
    Args:
        project_id: Project ID or path
        source_branch: Source branch name
        target_branch: Target branch name
        title: Merge request title
        description: Merge request description
        labels: Comma-separated list of label names
        assignee_id: User ID to assign the MR to
        remove_source_branch: Remove source branch when merged
    
    Returns:
        Created merge request details
    """
    data = {
        "source_branch": source_branch,
        "target_branch": target_branch,
        "title": title,
        "remove_source_branch": remove_source_branch,
    }
    
    if description:
        data["description"] = description
    if labels:
        data["labels"] = labels
    if assignee_id:
        data["assignee_id"] = assignee_id
    
    response = await client.post(
        f"/projects/{project_id}/merge_requests",
        json=data,
        headers=get_auth_headers()
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def update_merge_request(
    project_id: str,
    merge_request_iid: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    state_event: Optional[str] = None,
    labels: Optional[str] = None,
    assignee_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Update an existing merge request
    
    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request IID
        title: New title
        description: New description
        state_event: State change (close, reopen, merge)
        labels: Comma-separated list of label names
        assignee_id: User ID to assign the MR to
    
    Returns:
        Updated merge request details
    """
    data = {}
    
    if title:
        data["title"] = title
    if description:
        data["description"] = description
    if state_event:
        data["state_event"] = state_event
    if labels:
        data["labels"] = labels
    if assignee_id is not None:
        data["assignee_id"] = assignee_id
    
    response = await client.put(
        f"/projects/{project_id}/merge_requests/{merge_request_iid}",
        json=data,
        headers=get_auth_headers()
    )
    response.raise_for_status()
    return response.json()


# ==================== PIPELINE TOOLS ====================

@mcp.tool()
async def list_pipelines(
    project_id: str,
    scope: Optional[str] = None,
    status: Optional[str] = None,
    ref: Optional[str] = None,
    per_page: int = 20,
    page: int = 1,
) -> Dict[str, Any]:
    """
    List GitLab CI/CD pipelines for a project
    
    Args:
        project_id: Project ID or path
        scope: Filter by scope (running, pending, finished, branches, tags)
        status: Filter by status (created, waiting_for_resource, preparing, pending, running, success, failed, canceled, skipped, manual, scheduled)
        ref: Filter by branch or tag
        per_page: Number of results per page (max 100)
        page: Page number
    
    Returns:
        List of pipelines
    """
    params = {
        "per_page": min(per_page, 100),
        "page": page,
    }
    
    if scope:
        params["scope"] = scope
    if status:
        params["status"] = status
    if ref:
        params["ref"] = ref
    
    response = await client.get(
        f"/projects/{project_id}/pipelines",
        params=params,
        headers=get_auth_headers()
    )
    response.raise_for_status()
    return {"pipelines": response.json(), "total": len(response.json())}


@mcp.tool()
async def get_pipeline(project_id: str, pipeline_id: int) -> Dict[str, Any]:
    """
    Get details of a specific pipeline
    
    Args:
        project_id: Project ID or path
        pipeline_id: Pipeline ID
    
    Returns:
        Pipeline details
    """
    response = await client.get(
        f"/projects/{project_id}/pipelines/{pipeline_id}",
        headers=get_auth_headers()
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def cancel_pipeline(project_id: str, pipeline_id: int) -> Dict[str, Any]:
    """
    Cancel a running pipeline
    
    Args:
        project_id: Project ID or path
        pipeline_id: Pipeline ID
    
    Returns:
        Cancelled pipeline details
    """
    response = await client.post(
        f"/projects/{project_id}/pipelines/{pipeline_id}/cancel",
        headers=get_auth_headers()
    )
    response.raise_for_status()
    return response.json()


# ==================== BRANCH TOOLS ====================

@mcp.tool()
async def list_branches(
    project_id: str,
    search: Optional[str] = None,
    per_page: int = 20,
    page: int = 1,
) -> Dict[str, Any]:
    """
    List branches in a project
    
    Args:
        project_id: Project ID or path
        search: Search branches by name
        per_page: Number of results per page (max 100)
        page: Page number
    
    Returns:
        List of branches
    """
    params = {
        "per_page": min(per_page, 100),
        "page": page,
    }
    
    if search:
        params["search"] = search
    
    response = await client.get(
        f"/projects/{project_id}/repository/branches",
        params=params,
        headers=get_auth_headers()
    )
    response.raise_for_status()
    return {"branches": response.json(), "total": len(response.json())}


@mcp.tool()
async def get_branch(project_id: str, branch: str) -> Dict[str, Any]:
    """
    Get details of a specific branch
    
    Args:
        project_id: Project ID or path
        branch: Branch name
    
    Returns:
        Branch details
    """
    response = await client.get(
        f"/projects/{project_id}/repository/branches/{branch}",
        headers=get_auth_headers()
    )
    response.raise_for_status()
    return response.json()


# ==================== USER TOOLS ====================

@mcp.tool()
async def get_current_user() -> Dict[str, Any]:
    """
    Get details of the currently authenticated user
    
    Returns:
        Current user details
    """
    response = await client.get("/user", headers=get_auth_headers())
    response.raise_for_status()
    return response.json()


@mcp.tool()
async def list_users(
    search: Optional[str] = None,
    username: Optional[str] = None,
    active: bool = True,
    per_page: int = 20,
    page: int = 1,
) -> Dict[str, Any]:
    """
    List GitLab users
    
    Args:
        search: Search users by name or email
        username: Filter by username
        active: Filter by active status
        per_page: Number of results per page (max 100)
        page: Page number
    
    Returns:
        List of users
    """
    params = {
        "active": active,
        "per_page": min(per_page, 100),
        "page": page,
    }
    
    if search:
        params["search"] = search
    if username:
        params["username"] = username
    
    response = await client.get("/users", params=params, headers=get_auth_headers())
    response.raise_for_status()
    return {"users": response.json(), "total": len(response.json())}


# ==================== GROUP TOOLS ====================

@mcp.tool()
async def list_groups(
    search: Optional[str] = None,
    owned: bool = False,
    all_available: bool = False,
    per_page: int = 20,
    page: int = 1,
) -> Dict[str, Any]:
    """
    List GitLab groups
    
    Args:
        search: Search groups by name
        owned: Return only groups owned by the authenticated user
        all_available: Show all available groups
        per_page: Number of results per page (max 100)
        page: Page number
    
    Returns:
        List of groups
    """
    params = {
        "per_page": min(per_page, 100),
        "page": page,
    }
    
    if search:
        params["search"] = search
    if owned:
        params["owned"] = "true"
    if all_available:
        params["all_available"] = "true"
    
    response = await client.get("/groups", params=params, headers=get_auth_headers())
    response.raise_for_status()
    return {"groups": response.json(), "total": len(response.json())}


@mcp.tool()
async def get_group(group_id: str) -> Dict[str, Any]:
    """
    Get details of a specific group
    
    Args:
        group_id: Group ID or path
    
    Returns:
        Group details
    """
    response = await client.get(f"/groups/{group_id}", headers=get_auth_headers())
    response.raise_for_status()
    return response.json()


# Main entry point for local development
# Note: FastMCP uses stdio protocol for MCP communication
# For Vercel deployment, see api/index.py for HTTP handler
if __name__ == "__main__":
    mcp.run()

