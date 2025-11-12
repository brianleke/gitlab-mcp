# Quick Start Guide

Get your GitLab MCP server up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Get a GitLab Token

1. Go to [GitLab Settings → Access Tokens](https://gitlab.com/-/user_settings/personal_access_tokens)
2. Create a new token with these scopes:
   - `api` (for full access)
   - Or `read_api` + `read_user` + `read_repository` (for read-only)
3. Copy the token

## Step 3: Set Environment Variables

**Option A: Export in terminal (temporary)**
```bash
export GITLAB_TOKEN="your_token_here"
export GITLAB_BASE_URL="https://gitlab.com/api/v4"
```

**Option B: Create .env file (recommended)**
```bash
cp env.example .env
# Then edit .env and add your tokens:
# - GITLAB_TOKEN: Your GitLab personal access token
# - SERVER_BEARER_TOKEN: (Optional) A bearer token to secure HTTP endpoints
```

## Step 4: Test the Server

```bash
python test_server.py
```

This will verify your connection to GitLab.

## Step 5: Connect Your MCP Client

### For Cursor:

1. Open Cursor Settings
2. Find MCP settings (or create `.cursor/mcp.json`)
3. Add:

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "python",
      "args": ["/Users/brainbetechuoh/Desktop/GitLab MCP/server.py"],
      "env": {
        "GITLAB_TOKEN": "your_token_here",
        "GITLAB_BASE_URL": "https://gitlab.com/api/v4"
      }
    }
  }
}
```

**Important:** Use the absolute path to `server.py`!

4. Restart Cursor

### For Claude Desktop:

1. Open the config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the same configuration as above

3. Restart Claude Desktop

## Step 6: Verify It Works

In your MCP client (Cursor or Claude), try asking:
- "List my GitLab projects"
- "Show me open issues in project X"
- "Create a new issue in project Y"

## Troubleshooting

**"Server not found"**
- Use absolute paths, not relative paths
- Make sure Python is in your PATH

**"Permission denied"**
- Make sure the script is readable: `chmod +r server.py`

**"401 Unauthorized"**
- Check your GitLab token is correct
- Make sure the token has the right scopes

**"Module not found"**
- Install dependencies: `pip install -r requirements.txt`

## Next Steps

- Read [README.md](README.md) for full documentation
- Read [DEPLOYMENT.md](DEPLOYMENT.md) to deploy to Vercel
- Explore all available tools in the README

Happy coding! 🚀

