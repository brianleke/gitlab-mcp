# GitLab MCP Server

A Model Context Protocol (MCP) server that integrates with GitLab, enabling AI assistants to interact with GitLab projects, issues, merge requests, pipelines, and more.

**Now available as a REST API on Vercel!** See [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment instructions.

## Features

- **Projects**: List, search, and get detailed information about GitLab projects
- **Issues**: List, view, and create issues
- **Merge Requests**: List and view merge requests
- **Pipelines**: View CI/CD pipeline status and history
- **Groups**: List and search GitLab groups
- **User Info**: Get information about the authenticated user

## Prerequisites

- Python 3.8 or higher
- A GitLab account with a Personal Access Token

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` and add your GitLab configuration:
   - `GITLAB_URL`: Your GitLab instance URL (default: `https://gitlab.com`)
   - `GITLAB_TOKEN`: Your GitLab Personal Access Token

### Getting a GitLab Personal Access Token

1. Go to your GitLab profile settings
2. Navigate to **Access Tokens** (or visit `https://gitlab.com/-/user_settings/personal_access_tokens`)
3. Create a new token with the following scopes:
   - `api` - Full API access
   - `read_api` - Read-only API access (if you only need read operations)
4. Copy the token and add it to your `.env` file

## Usage

### Running the Server

The server uses stdio (standard input/output) for communication, which is the standard way MCP servers communicate with clients.

```bash
python server.py
```

### With MCP Clients

To use this server with an MCP client (like Claude Desktop), add it to your MCP configuration:

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "python",
      "args": ["/path/to/GitLab MCP/server.py"],
      "env": {
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_TOKEN": "your_token_here"
      }
    }
  }
}
```

## Available Tools

### `list_projects`
List GitLab projects with optional filters.

**Parameters:**
- `owned` (boolean): Only return projects owned by the current user
- `starred` (boolean): Only return starred projects
- `search` (string): Search for projects by name
- `limit` (integer): Maximum number of projects to return (default: 20)

### `get_project`
Get detailed information about a specific project.

**Parameters:**
- `project_id` (string, required): Project ID or path (e.g., "group/project" or numeric ID)

### `list_issues`
List issues from a GitLab project.

**Parameters:**
- `project_id` (string, required): Project ID or path
- `state` (string): Filter by state - "opened", "closed", or "all" (default: "opened")
- `labels` (string): Comma-separated list of label names
- `limit` (integer): Maximum number of issues to return (default: 20)

### `get_issue`
Get detailed information about a specific issue.

**Parameters:**
- `project_id` (string, required): Project ID or path
- `issue_iid` (integer, required): Issue IID (internal ID within the project)

### `create_issue`
Create a new issue in a GitLab project.

**Parameters:**
- `project_id` (string, required): Project ID or path
- `title` (string, required): Issue title
- `description` (string): Issue description
- `labels` (string): Comma-separated list of labels

### `list_merge_requests`
List merge requests from a GitLab project.

**Parameters:**
- `project_id` (string, required): Project ID or path
- `state` (string): Filter by state - "opened", "closed", "merged", or "all" (default: "opened")
- `limit` (integer): Maximum number of MRs to return (default: 20)

### `get_merge_request`
Get detailed information about a specific merge request.

**Parameters:**
- `project_id` (string, required): Project ID or path
- `mr_iid` (integer, required): Merge request IID

### `list_pipelines`
List CI/CD pipelines for a GitLab project.

**Parameters:**
- `project_id` (string, required): Project ID or path
- `status` (string): Filter by status - "running", "pending", "success", "failed", "canceled", "skipped"
- `limit` (integer): Maximum number of pipelines to return (default: 20)

### `list_groups`
List GitLab groups.

**Parameters:**
- `search` (string): Search for groups by name
- `limit` (integer): Maximum number of groups to return (default: 20)

### `get_user_info`
Get information about the current authenticated user.

**Parameters:** None

## Available Resources

- `gitlab://user` - Current authenticated user information
- `gitlab://projects` - List of all accessible projects
- `gitlab://groups` - List of all accessible groups

## Error Handling

The server includes error handling and will return JSON error messages if operations fail. Common issues:

- **Missing Token**: Ensure `GITLAB_TOKEN` is set in your environment
- **Invalid Token**: Verify your token is valid and has the required scopes
- **Network Issues**: Check your GitLab URL and network connectivity
- **Permission Errors**: Ensure your token has the necessary permissions for the operations you're trying to perform

## Development

To extend the server with additional functionality:

1. Add new tools in the `list_tools()` function
2. Implement tool handlers in the `call_tool()` function
3. Add new resources in `list_resources()` and `read_resource()`

## License

This project is provided as-is for use with the Model Context Protocol.

## REST API Deployment (Vercel)

This MCP server can also be deployed as a REST API on Vercel. See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy

1. Push your code to a Git repository
2. Import the repository in [Vercel](https://vercel.com/new)
3. Set environment variables:
   - `GITLAB_URL`: Your GitLab instance URL
   - `GITLAB_TOKEN`: Your GitLab Personal Access Token
4. Deploy!

### API Endpoints

Once deployed, access the API at `https://your-project.vercel.app/api/`:

- `GET /api/` - API documentation
- `GET /api/user` - Current user info
- `GET /api/projects` - List projects
- `GET /api/issues?project_id=<id>` - List issues
- `POST /api/issues` - Create issue
- `GET /api/merge_requests?project_id=<id>` - List merge requests
- `GET /api/pipelines?project_id=<id>` - List pipelines
- `GET /api/groups` - List groups

See [DEPLOYMENT.md](./DEPLOYMENT.md) for full API documentation and examples.

## Support

For issues or questions:
- Check the [GitLab API documentation](https://docs.gitlab.com/ee/api/)
- Review the [python-gitlab library documentation](https://python-gitlab.readthedocs.io/)
- See [DEPLOYMENT.md](./DEPLOYMENT.md) for Vercel deployment help

