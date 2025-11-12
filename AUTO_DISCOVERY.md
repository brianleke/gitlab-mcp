# Auto-Discovery of MCP Tools

The `mcp_client_server.py` now automatically discovers tools from your REST API documentation!

## How It Works

1. **Fetches API Documentation**: On startup, the MCP server calls your `/api/` endpoint to get the API documentation
2. **Parses Endpoints**: It extracts all endpoint definitions, methods, parameters, and descriptions
3. **Converts to MCP Tools**: Each API endpoint is automatically converted to an MCP tool
4. **Caches Results**: The discovered tools are cached for performance

## Benefits

✅ **No Manual Updates**: When you add new endpoints to your API, they automatically become available as MCP tools

✅ **Always in Sync**: The tools always match your actual API endpoints

✅ **Self-Documenting**: Tool descriptions come directly from your API documentation

✅ **Type Inference**: The system automatically infers parameter types (string, integer, boolean, enum)

## How to Use

1. **Deploy your API** to Vercel with the `/api/` documentation endpoint
2. **Configure the MCP server** with your API URL:
   ```json
   {
     "mcpServers": {
       "gitlab-api": {
         "command": "python3",
         "args": ["/path/to/mcp_client_server.py"],
         "env": {
           "GITLAB_API_URL": "https://your-project.vercel.app/api",
           "API_BEARER_TOKEN": "your-token"
         }
       }
     }
   }
   ```
3. **Restart your MCP client** - tools will be auto-discovered!

## Adding New Endpoints

When you add a new endpoint to your REST API:

1. Add it to the `/api/` documentation endpoint in `api/index.py`
2. Deploy to Vercel
3. Restart your MCP client
4. The new tool will automatically appear!

No need to modify `mcp_client_server.py` - it discovers everything automatically.

## Example

If your API has:
```json
{
  "/api/user": {
    "method": "GET",
    "description": "Get current authenticated user information"
  }
}
```

The MCP server will automatically create:
- Tool name: `user`
- Description: "Get current authenticated user information"
- Parameters: (none, based on the endpoint definition)

## Fallback

If API discovery fails (e.g., API is down), the server falls back to a minimal set of hardcoded tools so it still works.

## Debugging

To see what tools were discovered, check the MCP client logs. The server will:
- Print warnings if API docs can't be fetched
- Use fallback tools if discovery fails
- Cache discovered tools for performance

