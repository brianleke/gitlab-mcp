# GitLab MCP Server

A Model Context Protocol (MCP) server for GitLab built with FastMCP, exposing GitLab API endpoints as MCP tools. This server can be deployed to Vercel and accessed by MCP clients like Cursor or Claude.

## Features

This MCP server provides tools for interacting with GitLab:

### Projects
- List projects with filtering and search
- Get project details
- Create new projects

### Issues
- List issues (project-specific or across all projects)
- Get issue details
- Create new issues
- Update existing issues

### Merge Requests
- List merge requests
- Get merge request details
- Create new merge requests
- Update merge requests

### Pipelines
- List CI/CD pipelines
- Get pipeline details
- Cancel running pipelines

### Branches
- List repository branches
- Get branch details

### Users
- Get current authenticated user
- List users with search

### Groups
- List groups
- Get group details

## Setup

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your GitLab personal access token:
   ```
   GITLAB_TOKEN=your_token_here
   GITLAB_BASE_URL=https://gitlab.com/api/v4
   ```

3. **Run the server:**
   ```bash
   python server.py
   ```

### Creating a GitLab Personal Access Token

1. Go to your GitLab profile settings
2. Navigate to "Access Tokens"
3. Create a new token with the following scopes:
   - `api` - Full API access
   - `read_api` - Read-only API access (if you only need read operations)
   - `read_user` - Read user information
   - `read_repository` - Read repository data
   - `write_repository` - Write repository data (for creating/updating)

## Deployment to Vercel

### Using Vercel CLI

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy:**
   ```bash
   vercel
   ```

3. **Set environment variables:**
   ```bash
   vercel env add GITLAB_TOKEN
   vercel env add GITLAB_BASE_URL
   ```

4. **Redeploy with environment variables:**
   ```bash
   vercel --prod
   ```

### Using Vercel Dashboard

1. Import your GitLab repository to Vercel
2. In project settings, add environment variables:
   - `GITLAB_TOKEN`: Your GitLab personal access token
   - `GITLAB_BASE_URL`: `https://gitlab.com/api/v4` (or your self-hosted instance URL)
   - `SERVER_BEARER_TOKEN`: (Optional) A bearer token to secure HTTP endpoints
3. Deploy the project

## Configuration

### Environment Variables

- `GITLAB_TOKEN` (required): Your GitLab personal access token
- `GITLAB_BASE_URL` (optional): GitLab API base URL (defaults to `https://gitlab.com/api/v4`)
- `SERVER_BEARER_TOKEN` (optional): Bearer token for securing the MCP server HTTP endpoints. If set, clients must provide this token in the `Authorization: Bearer <token>` header when accessing HTTP endpoints (e.g., Vercel deployment). Leave empty to disable bearer token authentication.

### Self-Hosted GitLab

If you're using a self-hosted GitLab instance, set `GITLAB_BASE_URL` to your instance's API URL:
```
GITLAB_BASE_URL=https://your-gitlab-instance.com/api/v4
```

## Connecting MCP Clients

**Important Note:** MCP servers use the stdio (standard input/output) protocol for communication. The Vercel deployment provides a health check endpoint, but MCP clients connect via stdio, not HTTP.

### Local Development (Recommended)

For local development, MCP clients connect directly to the server via stdio:

#### Cursor

Add to your Cursor MCP settings (usually in `.cursor/mcp.json` or Cursor settings):

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "python",
      "args": ["/absolute/path/to/GitLab MCP/server.py"],
      "env": {
        "GITLAB_TOKEN": "your_token_here",
        "GITLAB_BASE_URL": "https://gitlab.com/api/v4"
      }
    }
  }
}
```

#### Claude Desktop

Add to your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "python",
      "args": ["/absolute/path/to/GitLab MCP/server.py"],
      "env": {
        "GITLAB_TOKEN": "your_token_here",
        "GITLAB_BASE_URL": "https://gitlab.com/api/v4"
      }
    }
  }
}
```

### Vercel Deployment

The Vercel deployment provides:
- Health check endpoint at `/` or `/health`
- Server metadata endpoint

**Note:** For MCP clients to use a Vercel-deployed server, you would need a bridge service that converts HTTP to stdio, or use the server locally as shown above.

To check if your Vercel deployment is working:

**Without bearer token (if SERVER_BEARER_TOKEN is not set):**
```bash
curl https://your-vercel-deployment-url.vercel.app/health
```

**With bearer token (if SERVER_BEARER_TOKEN is set):**
```bash
curl -H "Authorization: Bearer your_server_bearer_token" \
  https://your-vercel-deployment-url.vercel.app/health
```

If the bearer token is missing or incorrect, you'll receive a `401 Unauthorized` response.

## Available Tools

### Project Tools
- `list_projects` - List GitLab projects with filtering
- `get_project` - Get project details
- `create_project` - Create a new project

### Issue Tools
- `list_issues` - List issues (project-specific or all)
- `get_issue` - Get issue details
- `create_issue` - Create a new issue
- `update_issue` - Update an existing issue

### Merge Request Tools
- `list_merge_requests` - List merge requests
- `get_merge_request` - Get merge request details
- `create_merge_request` - Create a new merge request
- `update_merge_request` - Update a merge request

### Pipeline Tools
- `list_pipelines` - List CI/CD pipelines
- `get_pipeline` - Get pipeline details
- `cancel_pipeline` - Cancel a running pipeline

### Branch Tools
- `list_branches` - List repository branches
- `get_branch` - Get branch details

### User Tools
- `get_current_user` - Get current authenticated user
- `list_users` - List users with search

### Group Tools
- `list_groups` - List groups
- `get_group` - Get group details

## Example Usage

Once connected to an MCP client, you can use natural language to interact with GitLab:

- "List all open issues in project mygroup/myproject"
- "Create a new issue titled 'Fix bug' in project 123"
- "Show me merge requests for the main branch"
- "Get details of pipeline 456 in project mygroup/myproject"

## License

MIT

