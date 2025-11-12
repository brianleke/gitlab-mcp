# Quick Start: Expose GitLab MCP Tools

Follow these steps to make the GitLab MCP tools available in your MCP client.

## Step 1: Get Your Absolute Path

First, find the absolute path to your `server.py` file:

```bash
cd "/Users/brainbetechuoh/Desktop/GitLab MCP"
pwd
```

This will output something like:
```
/Users/brainbetechuoh/Desktop/GitLab MCP
```

So your full path to server.py is:
```
/Users/brainbetechuoh/Desktop/GitLab MCP/server.py
```

## Step 2: Configure in Your MCP Client

### Option A: Cursor

1. **Open Cursor Settings**
   - Press `Cmd+,` (Mac) or `Ctrl+,` (Windows/Linux)
   - Or go to: Cursor → Settings

2. **Navigate to MCP Settings**
   - Search for "MCP" in settings
   - Or go to: Features → MCP
   - Or: Tools & Integrations → MCP Tools

3. **Add MCP Server**
   - Click "Add MCP Server" or "Edit MCP Configuration"
   - This opens your MCP config file (usually `~/.cursor/mcp.json` or similar)

4. **Add This Configuration**

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "python3",
      "args": [
        "/Users/brainbetechuoh/Desktop/GitLab MCP/server.py"
      ],
      "env": {
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_TOKEN": "glpat-HXs5YgO77LCCMuFdkweioW86MQp1OmlyaTY3Cw.01.12167twc3"
      }
    }
  }
}
```

**Important**: Replace the path with your actual absolute path from Step 1!

5. **Save and Restart**
   - Save the configuration file
   - **Restart Cursor completely** (quit and reopen)

### Option B: Claude Desktop

1. **Open Claude Desktop Settings**
   - Click the gear icon or go to Settings

2. **Edit MCP Configuration**
   - Go to Developer → Edit Config
   - Or manually edit: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)
   - Or: `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

3. **Add This Configuration**

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "python3",
      "args": [
        "/Users/brainbetechuoh/Desktop/GitLab MCP/server.py"
      ],
      "env": {
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_TOKEN": "glpat-HXs5YgO77LCCMuFdkweioW86MQp1OmlyaTY3Cw.01.12167twc3"
      }
    }
  }
}
```

4. **Save and Restart Claude Desktop**

## Step 3: Verify It's Working

### In Cursor:
1. Open a chat
2. Type: "What GitLab tools do you have access to?"
3. The AI should list tools like:
   - `get_user_info`
   - `list_projects`
   - `list_issues`
   - `create_issue`
   - etc.

### In Claude Desktop:
1. Start a new conversation
2. Ask: "Can you show me my GitLab user information?"
3. It should use the `get_user_info` tool

## Troubleshooting

### Tools Still Not Showing?

1. **Check the Path**
   ```bash
   # Verify the path exists
   ls -la "/Users/brainbetechuoh/Desktop/GitLab MCP/server.py"
   ```

2. **Test Python Command**
   ```bash
   # Make sure python3 works
   python3 --version
   
   # Test if the server can start
   python3 "/Users/brainbetechuoh/Desktop/GitLab MCP/server.py"
   # (It will wait for input - press Ctrl+C to exit)
   ```

3. **Check Dependencies**
   ```bash
   pip3 install mcp python-gitlab
   ```

4. **Run Diagnostic Script**
   ```bash
   python3 "/Users/brainbetechuoh/Desktop/GitLab MCP/test_mcp_server.py"
   ```
   This will check everything and generate the correct config for you.

5. **Check MCP Client Logs**
   - **Cursor**: View → Developer → Toggle Developer Tools → Console
   - **Claude Desktop**: Check the Developer console for errors

6. **Verify Environment Variables**
   - Make sure `GITLAB_TOKEN` is set in the `env` section
   - The token should start with `glpat-` for GitLab.com

### Common Issues

**Issue**: "Command not found: python3"
- **Solution**: Try `python` instead of `python3`, or use full path: `/usr/bin/python3`

**Issue**: "Permission denied"
- **Solution**: 
  ```bash
  chmod +x "/Users/brainbetechuoh/Desktop/GitLab MCP/server.py"
  ```

**Issue**: "Module not found: mcp"
- **Solution**: 
  ```bash
  pip3 install mcp python-gitlab
  ```

**Issue**: "GITLAB_TOKEN environment variable is required"
- **Solution**: Make sure the token is in the `env` section of your MCP config

## Alternative: Using Virtual Environment

If you're using a virtual environment:

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "/path/to/venv/bin/python",
      "args": [
        "/Users/brainbetechuoh/Desktop/GitLab MCP/server.py"
      ],
      "env": {
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_TOKEN": "your_token_here"
      }
    }
  }
}
```

## Quick Test

After configuration, test with:

```bash
# Run the diagnostic script
python3 "/Users/brainbetechuoh/Desktop/GitLab MCP/test_mcp_server.py"
```

This will:
- Check all dependencies
- Test GitLab connection
- Generate the correct configuration for you
- Show you exactly what to copy

## What Tools Will Be Available?

Once configured, you'll have access to:

1. **get_user_info** - Get your GitLab user information
2. **list_projects** - List your GitLab projects
3. **get_project** - Get details about a specific project
4. **list_issues** - List issues from a project
5. **get_issue** - Get details about a specific issue
6. **create_issue** - Create a new issue
7. **list_merge_requests** - List merge requests
8. **get_merge_request** - Get merge request details
9. **list_pipelines** - List CI/CD pipelines
10. **list_groups** - List GitLab groups

## Next Steps

Once the tools are visible:
- Ask your AI: "List my GitLab projects"
- Try: "Show me my GitLab user info"
- Test: "List issues from project X"

The AI will automatically use the appropriate MCP tools!

