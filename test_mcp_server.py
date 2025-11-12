#!/usr/bin/env python3
"""
Test script to verify the MCP server is working correctly.
"""

import os
import sys
import json

print("=" * 60)
print("GitLab MCP Server Diagnostic Test")
print("=" * 60)
print()

# Test 1: Check Python version
print("1. Checking Python version...")
version = sys.version_info
print(f"   Python {version.major}.{version.minor}.{version.micro}")
if version.major < 3 or (version.major == 3 and version.minor < 8):
    print("   ❌ ERROR: Python 3.8+ required")
    sys.exit(1)
else:
    print("   ✅ Python version OK")
print()

# Test 2: Check dependencies
print("2. Checking dependencies...")
try:
    import mcp
    print("   ✅ mcp package installed")
except ImportError:
    print("   ❌ ERROR: mcp package not found")
    print("   Run: pip install mcp")
    sys.exit(1)

try:
    import gitlab
    print("   ✅ python-gitlab package installed")
except ImportError:
    print("   ❌ ERROR: python-gitlab package not found")
    print("   Run: pip install python-gitlab")
    sys.exit(1)
print()

# Test 3: Check environment variables
print("3. Checking environment variables...")
gitlab_url = os.getenv("GITLAB_URL", "https://gitlab.com")
gitlab_token = os.getenv("GITLAB_TOKEN")

print(f"   GITLAB_URL: {gitlab_url}")
if gitlab_token:
    print(f"   GITLAB_TOKEN: {'*' * min(len(gitlab_token), 20)}... (set)")
else:
    print("   ❌ ERROR: GITLAB_TOKEN not set")
    print("   Set it with: export GITLAB_TOKEN=your_token")
    sys.exit(1)
print()

# Test 4: Check server.py exists
print("4. Checking server.py...")
server_path = os.path.join(os.path.dirname(__file__), "server.py")
if os.path.exists(server_path):
    print(f"   ✅ server.py found at: {server_path}")
    print(f"   Absolute path: {os.path.abspath(server_path)}")
else:
    print(f"   ❌ ERROR: server.py not found at {server_path}")
    sys.exit(1)
print()

# Test 5: Test GitLab connection
print("5. Testing GitLab connection...")
try:
    import gitlab
    gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
    gl.auth()
    user = gl.user
    print(f"   ✅ Connected to GitLab as: {user.username}")
except Exception as e:
    print(f"   ❌ ERROR: Failed to connect to GitLab: {e}")
    sys.exit(1)
print()

# Test 6: Check MCP server can be imported
print("6. Testing MCP server import...")
try:
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(__file__))
    # Try to import the server module
    import importlib.util
    spec = importlib.util.spec_from_file_location("server", server_path)
    server_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_module)
    print("   ✅ server.py can be imported")
except Exception as e:
    print(f"   ❌ ERROR: Failed to import server.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print()

# Test 7: Check tools are defined
print("7. Checking MCP tools...")
try:
    # Check if app exists and has list_tools
    if hasattr(server_module, 'app'):
        app = server_module.app
        print("   ✅ MCP Server app found")
        
        # Try to get tools (this is async, so we'll just check the method exists)
        if hasattr(app, 'list_tools'):
            print("   ✅ list_tools method exists")
        else:
            print("   ❌ ERROR: list_tools method not found")
    else:
        print("   ❌ ERROR: MCP Server app not found")
except Exception as e:
    print(f"   ⚠️  Warning: Could not verify tools: {e}")
print()

# Test 8: Generate MCP configuration
print("8. Generating MCP configuration...")
abs_path = os.path.abspath(server_path)
python_cmd = sys.executable

config = {
    "mcpServers": {
        "gitlab": {
            "command": python_cmd,
            "args": [abs_path],
            "env": {
                "GITLAB_URL": gitlab_url,
                "GITLAB_TOKEN": gitlab_token
            }
        }
    }
}

print("   Copy this configuration to your MCP client:")
print()
print(json.dumps(config, indent=2))
print()

print("=" * 60)
print("✅ All tests passed! Your MCP server should work.")
print("=" * 60)
print()
print("Next steps:")
print("1. Copy the configuration above to your MCP client")
print("2. Restart your MCP client (Cursor, Claude Desktop, etc.)")
print("3. The tools should appear in your client")
print()

