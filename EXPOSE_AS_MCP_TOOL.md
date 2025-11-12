# Expose GitLab REST API as MCP Tools

This guide shows you how to use the MCP client server (`mcp_client_server.py`) to expose your Vercel-deployed GitLab REST API as MCP tools.

## Architecture

```
MCP Client (Cursor/Claude) 
    ↓
MCP Server (mcp_client_server.py)
    ↓ HTTP Requests
Vercel REST API (your-project.vercel.app/api)
    ↓
GitLab API
```

## Setup Steps

### 1. Deploy Your REST API to Vercel

First, make sure your REST API is deployed to Vercel:
- Follow the [DEPLOYMENT.md](./DEPLOYMENT.md) guide
- Note your Vercel deployment URL (e.g., `https://your-project.vercel.app`)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `mcp` - MCP server framework
- `requests` - For making HTTP requests to your API

### 3. Configure Environment Variables

Set these environment variables:

```bash
# Your Vercel API base URL
export GITLAB_API_URL=https://your-project.vercel.app/api

# Bearer token for API authentication (from API_BEARER_TOKENS or GITLAB_TOKEN)
export API_BEARER_TOKEN=your-bearer-token-here
```

Or create a `.env` file:
```bash
GITLAB_API_URL=https://your-project.vercel.app/api
API_BEARER_TOKEN=your-bearer-token-here
```

### 4. Configure in Your MCP Client

#### For Cursor:

1. Open Cursor Settings (`Cmd+,` or `Ctrl+,`)
2. Go to Features → MCP (or Tools & Integrations → MCP Tools)
3. Click "Add MCP Server" or "Edit MCP Configuration"
4. Add this configuration:

```json
{
  "mcpServers": {
    "gitlab-api": {
      "command": "python3",
      "args": [
        "/Users/brainbetechuoh/Desktop/GitLab MCP/mcp_client_server.py"
      ],
      "env": {
        "GITLAB_API_URL": "https://your-project.vercel.app/api",
        "API_BEARER_TOKEN": "your-bearer-token-here"
      }
    }
  }
}
```

**Important**: 
- Replace the path with your absolute path to `mcp_client_server.py`
- Replace `your-project.vercel.app` with your actual Vercel URL
- Use the bearer token you configured in Vercel (from `API_BEARER_TOKENS`)

#### For Claude Desktop:

1. Settings → Developer → Edit Config
2. Add the same configuration as above
3. Save and restart

### 5. Restart Your MCP Client

**Important**: You must completely restart Cursor/Claude Desktop for the changes to take effect.

### 6. Verify It Works

After restarting, ask your AI:
- "What GitLab tools do you have access to?"
- "Get my GitLab user information"
- "List my GitLab projects"

The tools should work by calling your Vercel API!

## Available Tools

The MCP server exposes these tools (which call your REST API):

1. **get_user_info** - Get GitLab user information
2. **list_projects** - List GitLab projects
3. **get_project** - Get specific project details
4. **list_issues** - List issues from a project
5. **get_issue** - Get specific issue details
6. **create_issue** - Create a new issue
7. **list_merge_requests** - List merge requests
8. **get_merge_request** - Get merge request details
9. **list_pipelines** - List CI/CD pipelines
10. **list_groups** - List GitLab groups

## Testing Locally

Before configuring in your MCP client, test the server:

```bash
# Set environment variables
export GITLAB_API_URL=https://your-project.vercel.app/api
export API_BEARER_TOKEN=your-token

# Test the server
python3 mcp_client_server.py
```

It should start and wait for input (this is normal for MCP servers).

## Troubleshooting

### Issue: "API request failed"

**Check:**
1. Is your Vercel API deployed and accessible?
   ```bash
   curl https://your-project.vercel.app/api/
   ```

2. Is the bearer token correct?
   - Must match one of the tokens in `API_BEARER_TOKENS` on Vercel
   - Or match `GITLAB_TOKEN` if `API_BEARER_TOKENS` is not set

3. Is the API URL correct?
   - Should end with `/api` (not `/api/`)
   - Should be your actual Vercel deployment URL

### Issue: "401 Unauthorized"

**Solution**: 
- Verify your bearer token is correct
- Check that `API_BEARER_TOKEN` is set in the MCP config's `env` section
- Make sure the token matches what's configured in Vercel

### Issue: Tools not appearing

**Check:**
1. Did you restart your MCP client completely?
2. Is the path to `mcp_client_server.py` absolute and correct?
3. Are dependencies installed? (`pip install mcp requests`)
4. Check MCP client logs for errors

### Issue: "Module not found: requests"

**Solution**:
```bash
pip install requests
```

## Example Configuration

Complete example for Cursor:

```json
{
  "mcpServers": {
    "gitlab-api": {
      "command": "python3",
      "args": [
        "/Users/brainbetechuoh/Desktop/GitLab MCP/mcp_client_server.py"
      ],
      "env": {
        "GITLAB_API_URL": "https://gitlab-mcp-api.vercel.app/api",
        "API_BEARER_TOKEN": "my-secret-bearer-token-123"
      }
    }
  }
}
```

## Benefits of This Approach

1. **Separation of Concerns**: API logic is separate from MCP server
2. **Scalability**: API can handle many requests, MCP server is lightweight
3. **Flexibility**: Same API can be used by web apps, mobile apps, and MCP tools
4. **Deployment**: API is deployed on Vercel (serverless, scalable)
5. **Security**: Bearer token authentication protects your API

## Next Steps

1. Deploy your API to Vercel
2. Configure the MCP client server
3. Add it to your MCP client configuration
4. Restart and test!

Your GitLab API is now accessible as MCP tools! 🎉

