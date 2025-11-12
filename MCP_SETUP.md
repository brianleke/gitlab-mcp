# MCP Server Setup Guide

This guide will help you set up and use the GitLab MCP server with your MCP client (Cursor, Claude Desktop, etc.).

## Prerequisites

1. Python 3.8 or higher
2. GitLab Personal Access Token
3. MCP-compatible client (Cursor, Claude Desktop, etc.)

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
# Create .env file or set environment variables
export GITLAB_URL=https://gitlab.com
export GITLAB_TOKEN=your_personal_access_token_here
```

## MCP Client Configuration

### For Cursor

1. Open Cursor Settings
2. Go to **Features** → **MCP** (or **Tools & Integrations** → **MCP Tools**)
3. Click **Add MCP Server** or edit your MCP configuration file
4. Add the following configuration:

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "python",
      "args": [
        "/absolute/path/to/GitLab MCP/server.py"
      ],
      "env": {
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_TOKEN": "your_personal_access_token_here"
      }
    }
  }
}
```

**Important**: Use the absolute path to `server.py`. For example:
- macOS/Linux: `/Users/yourusername/Desktop/GitLab MCP/server.py`
- Windows: `C:\Users\yourusername\Desktop\GitLab MCP\server.py`

### For Claude Desktop

1. Open Claude Desktop
2. Go to Settings → Developer → Edit Config
3. Edit the MCP configuration file (usually `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS)
4. Add:

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "python3",
      "args": [
        "/absolute/path/to/GitLab MCP/server.py"
      ],
      "env": {
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_TOKEN": "your_personal_access_token_here"
      }
    }
  }
}
```

### Alternative: Using Python with venv

If you're using a virtual environment:

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "/path/to/venv/bin/python",
      "args": [
        "/absolute/path/to/GitLab MCP/server.py"
      ],
      "env": {
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_TOKEN": "your_personal_access_token_here"
      }
    }
  }
}
```

## Testing the MCP Server

### Test 1: Run the server directly

```bash
python server.py
```

The server should start and wait for input (it uses stdio). If you see errors, check:
- Python version: `python --version` (should be 3.8+)
- Dependencies: `pip list | grep mcp` and `pip list | grep python-gitlab`
- Environment variables: `echo $GITLAB_TOKEN`

### Test 2: Use MCP Inspector

Install the MCP Inspector:
```bash
npm install -g @modelcontextprotocol/inspector
```

Run the inspector:
```bash
mcp-inspector python server.py
```

This will open a web interface where you can:
- See all available tools
- Test tool calls
- View resources

### Test 3: Check MCP Client Logs

In Cursor:
1. Open Developer Tools (View → Developer → Toggle Developer Tools)
2. Check the Console for MCP-related errors
3. Look for messages about the GitLab MCP server

In Claude Desktop:
- Check the logs in the Developer console
- Look for MCP server connection messages

## Available Tools

Once properly configured, you should see these tools in your MCP client:

1. **get_user_info** - Get current authenticated user information
2. **list_projects** - List GitLab projects
3. **get_project** - Get specific project details
4. **list_issues** - List issues from a project
5. **get_issue** - Get specific issue details
6. **create_issue** - Create a new issue
7. **list_merge_requests** - List merge requests
8. **get_merge_request** - Get specific merge request details
9. **list_pipelines** - List CI/CD pipelines
10. **list_groups** - List GitLab groups

## Troubleshooting

### Issue: Tools not showing up

**Possible causes:**

1. **Wrong path**: Make sure you're using the absolute path to `server.py`
   ```bash
   # Get absolute path
   cd "/Users/brainbetechuoh/Desktop/GitLab MCP"
   pwd
   ```

2. **Python not found**: Make sure `python` or `python3` is in your PATH
   ```bash
   which python
   which python3
   ```

3. **Missing dependencies**: Install all requirements
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables not set**: The server needs `GITLAB_TOKEN` to work
   ```bash
   echo $GITLAB_TOKEN
   ```

5. **Server not executable**: Make sure the file is readable
   ```bash
   chmod +x server.py
   ```

### Issue: "GITLAB_TOKEN environment variable is required"

**Solution**: Set the token in your MCP configuration's `env` section, or export it:
```bash
export GITLAB_TOKEN=your_token_here
```

### Issue: Import errors

**Solution**: Make sure all dependencies are installed:
```bash
pip install mcp python-gitlab
```

### Issue: Server starts but tools don't appear

**Check:**
1. Restart your MCP client after configuration changes
2. Check MCP client logs for errors
3. Verify the server is actually running (check process list)
4. Try using the MCP Inspector to test the server directly

### Issue: Permission denied

**Solution**: 
```bash
chmod +x server.py
```

Or use `python server.py` instead of `./server.py`

## Verification Steps

1. **Check server.py exists and is readable:**
   ```bash
   ls -la "/Users/brainbetechuoh/Desktop/GitLab MCP/server.py"
   ```

2. **Test Python can run it:**
   ```bash
   python "/Users/brainbetechuoh/Desktop/GitLab MCP/server.py"
   ```
   (It will wait for input - this is normal. Press Ctrl+C to exit)

3. **Verify environment variables:**
   ```bash
   GITLAB_TOKEN=test python -c "import os; print(os.getenv('GITLAB_TOKEN'))"
   ```

4. **Check MCP client configuration:**
   - Verify JSON syntax is correct
   - Check paths are absolute
   - Ensure environment variables are set

## Example MCP Configuration

Here's a complete example for Cursor:

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
        "GITLAB_TOKEN": "glpat-xxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

## Getting Help

If tools still don't appear:

1. **Check MCP client logs** - Look for error messages
2. **Test with MCP Inspector** - This will show if the server itself works
3. **Verify server.py** - Make sure it hasn't been modified incorrectly
4. **Check Python version** - Must be 3.8 or higher
5. **Verify dependencies** - Run `pip install -r requirements.txt` again

## Next Steps

Once the tools appear:
- Try asking your AI assistant: "List my GitLab projects"
- Use: "Get information about my GitLab user"
- Test: "List issues from project X"

The tools should be available in your MCP client's tool list!

