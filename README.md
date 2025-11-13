# GitLab MCP Server

A Model Context Protocol (MCP) server deployable on Vercel that exposes GitLab APIs as tools. This server allows AI assistants and other MCP clients to interact with GitLab projects, issues, merge requests, branches, commits, and more.

## Features

This MCP server provides the following GitLab API tools:

- **Projects**: List and get project details
- **Issues**: List, get, and create issues
- **Merge Requests**: List and get merge request details
- **Branches**: List project branches
- **Commits**: List project commits
- **Users**: Get authenticated user information
- **Groups**: List GitLab groups

## Prerequisites

- Node.js 18+ installed
- A Vercel account
- A GitLab account with a personal access token

## Getting Started

### 1. Clone and Install

```bash
npm install
```

### 2. Get a GitLab Personal Access Token

1. Go to your GitLab account settings
2. Navigate to "Access Tokens" or "Personal Access Tokens"
3. Create a new token with the following scopes:
   - `api` - Full API access
   - `read_api` - Read-only API access (if you only need read operations)

### 3. Configure Environment Variables

**Required:** Set the following environment variables in Vercel:

1. **`GITLAB_PRIVATE_TOKEN`** - Your GitLab personal access token:
```bash
vercel env add GITLAB_PRIVATE_TOKEN
```

2. **`MCP_BEARER_TOKEN`** - A secure token to protect access to your MCP server:
```bash
vercel env add MCP_BEARER_TOKEN
```

Generate a secure random token using:
```bash
openssl rand -hex 32
```

Or use any secure random string generator.

**Optional:** If you're using a self-hosted GitLab instance, also set the `GITLAB_API_URL` environment variable:

```bash
vercel env add GITLAB_API_URL
```

Or set these in the Vercel dashboard under Project Settings > Environment Variables.

### 4. Deploy to Vercel

```bash
# Install Vercel CLI if you haven't already
npm i -g vercel

# Deploy
vercel deploy
```

Or connect your repository to Vercel through the Vercel dashboard for automatic deployments.

### 5. Configure Your MCP Client

Once deployed, configure your MCP client to connect to your Vercel deployment. The endpoint will be:

```
https://your-project.vercel.app/api
```

**Authentication:** The MCP server is protected by Bearer token authentication. Include the `MCP_BEARER_TOKEN` in the `Authorization` header when making requests:

```
Authorization: Bearer your-mcp-bearer-token-here
```

The GitLab token is configured via environment variables and used automatically for GitLab API calls, so you don't need to pass it when calling tools.

## Available Tools

### `list_gitlab_projects`
Lists all projects accessible to the authenticated user or in a specific group.

**Parameters:**
- `groupId` (optional): Group ID to filter projects
- `owned` (optional): Limit to owned projects
- `starred` (optional): Limit to starred projects
- `search` (optional): Search projects by name
- `perPage` (optional): Results per page
- `page` (optional): Page number

### `get_gitlab_project`
Gets detailed information about a specific project.

**Parameters:**
- `projectId` (required): Project ID or path (e.g., "group/project")

### `list_gitlab_issues`
Lists issues for a project.

**Parameters:**
- `projectId` (required): Project ID or path
- `state` (optional): Filter by state (opened, closed, all)
- `labels` (optional): Comma-separated label names
- `assigneeId` (optional): Filter by assignee
- `milestone` (optional): Filter by milestone
- `search` (optional): Search issues
- `perPage` (optional): Results per page
- `page` (optional): Page number

### `get_gitlab_issue`
Gets detailed information about a specific issue.

**Parameters:**
- `projectId` (required): Project ID or path
- `issueIid` (required): Issue IID (internal ID)

### `create_gitlab_issue`
Creates a new issue in a project.

**Parameters:**
- `projectId` (required): Project ID or path
- `title` (required): Issue title
- `description` (optional): Issue description
- `labels` (optional): Comma-separated label names
- `assigneeIds` (optional): Array of user IDs
- `milestoneId` (optional): Milestone ID
- `dueDate` (optional): Due date (YYYY-MM-DD)

### `list_gitlab_merge_requests`
Lists merge requests for a project.

**Parameters:**
- `projectId` (required): Project ID or path
- `state` (optional): Filter by state (opened, closed, locked, merged, all)
- `labels` (optional): Comma-separated label names
- `authorId` (optional): Filter by author
- `assigneeId` (optional): Filter by assignee
- `search` (optional): Search MRs
- `perPage` (optional): Results per page
- `page` (optional): Page number

### `get_gitlab_merge_request`
Gets detailed information about a specific merge request.

**Parameters:**
- `projectId` (required): Project ID or path
- `mergeRequestIid` (required): MR IID (internal ID)

### `list_gitlab_branches`
Lists branches for a project.

**Parameters:**
- `projectId` (required): Project ID or path
- `search` (optional): Search branches by name
- `perPage` (optional): Results per page
- `page` (optional): Page number

### `list_gitlab_commits`
Lists commits for a project.

**Parameters:**
- `projectId` (required): Project ID or path
- `refName` (optional): Branch, tag, or commit SHA
- `since` (optional): Only commits after this date (ISO 8601)
- `until` (optional): Only commits before this date (ISO 8601)
- `path` (optional): Only commits affecting this path
- `author` (optional): Filter by author email
- `perPage` (optional): Results per page
- `page` (optional): Page number

### `get_gitlab_user`
Gets information about the authenticated user.

**Parameters:**
None

### `list_gitlab_groups`
Lists GitLab groups accessible to the authenticated user.

**Parameters:**
- `search` (optional): Search groups by name or path
- `owned` (optional): Limit to owned groups
- `perPage` (optional): Results per page
- `page` (optional): Page number

## Security Considerations

1. **MCP Server Protection**: The MCP server requires a Bearer token for authentication. This protects your server from unauthorized access. Generate a strong, random token for `MCP_BEARER_TOKEN`.

2. **Store tokens securely**: Both the GitLab token and MCP Bearer token are stored in Vercel's environment variables, which are encrypted and never exposed in your code or logs.

3. **Never commit tokens**: Never commit your `.env` file or hardcode tokens in your code. Use Vercel's environment variables feature.

4. **Token scopes**: Use the minimum required token scopes for your GitLab token. For read-only operations, use `read_api` instead of `api`.

5. **HTTPS only**: Always use HTTPS when deploying to Vercel to ensure secure communication.

6. **Rate limiting**: Be aware of GitLab's API rate limits. The server will pass through any rate limit errors from GitLab.

7. **Separate concerns**: The `MCP_BEARER_TOKEN` is for protecting access to the MCP server, while `GITLAB_PRIVATE_TOKEN` is used for GitLab API authentication. Keep them separate and secure.

## Local Development

To test locally:

```bash
# Install dependencies
npm install

# Run Vercel dev server
npm run dev
```

The server will be available at `http://localhost:3000/api`.

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check that your GitLab private token is valid and has the correct scopes.

2. **404 Not Found**: Verify the project ID or path is correct. Project paths should be URL-encoded (e.g., "group%2Fproject").

3. **Rate Limit Errors**: GitLab has rate limits. Wait before retrying or use a token with higher rate limits.

4. **CORS Issues**: If accessing from a browser, ensure CORS is properly configured in your MCP client.

## License

MIT

