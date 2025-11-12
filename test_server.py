"""
Simple test script to verify the MCP server is working
Run this to test the server locally before connecting MCP clients
"""

import os
import sys
import asyncio

# Set test environment variables if not set
if not os.getenv("GITLAB_TOKEN"):
    print("Warning: GITLAB_TOKEN not set. Some tests may fail.")
    print("Set it with: export GITLAB_TOKEN=your_token")

# Import the server
from server import mcp, get_auth_headers, client

async def test_connection():
    """Test basic connection to GitLab API"""
    try:
        # Test getting current user
        response = await client.get("/user", headers=get_auth_headers())
        if response.status_code == 200:
            user = response.json()
            print(f"✓ Connected to GitLab as: {user.get('username', 'Unknown')}")
            return True
        else:
            print(f"✗ Connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

async def test_tools():
    """List available MCP tools"""
    print("\nAvailable MCP Tools:")
    print("-" * 50)
    
    # FastMCP stores tools in the mcp instance
    # Try to get tools list
    if hasattr(mcp, '_tools'):
        for tool_name in mcp._tools.keys():
            print(f"  - {tool_name}")
    else:
        # Fallback: list all non-private attributes that might be tools
        print("  (Unable to list tools - server may need to be started)")
    
    print()

def main():
    """Run tests"""
    print("GitLab MCP Server Test")
    print("=" * 50)
    
    # Test connection
    print("\n1. Testing GitLab API connection...")
    asyncio.run(test_connection())
    
    # List tools
    print("\n2. Checking available tools...")
    asyncio.run(test_tools())
    
    print("\n" + "=" * 50)
    print("Test complete!")
    print("\nTo start the MCP server, run: python server.py")
    print("The server will wait for MCP client connections via stdio.")

if __name__ == "__main__":
    main()

