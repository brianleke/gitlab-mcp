# Quick Start Guide

## 1. Install Dependencies

```bash
npm install
```

## 2. Get Your GitLab Token

1. Go to https://gitlab.com/-/user_settings/personal_access_tokens
2. Create a new token with `api` scope
3. Copy the token (you'll need it for the next step)

## 3. Set Environment Variables in Vercel

Before deploying, set the required environment variables:

```bash
# Install Vercel CLI globally (if not already installed)
npm install -g vercel

# Set the GitLab token
vercel env add GITLAB_PRIVATE_TOKEN
# Paste your GitLab token when prompted

# Generate and set the MCP Bearer token
# First, generate a secure token:
openssl rand -hex 32

# Then set it:
vercel env add MCP_BEARER_TOKEN
# Paste the generated token when prompted
```

Or set these in the Vercel dashboard under Project Settings > Environment Variables.

## 4. Deploy to Vercel

```bash
# Deploy
vercel
```

Follow the prompts to link your project or create a new one.

## 5. Test Your Deployment

Once deployed, your MCP server will be available at:
```
https://your-project.vercel.app/api
```

You can test it using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector@latest https://your-project.vercel.app/api
```

## 6. Configure Your MCP Client

Add your deployment URL to your MCP client configuration. Include the `MCP_BEARER_TOKEN` in the `Authorization` header:

```
Authorization: Bearer your-mcp-bearer-token-here
```

Example using curl:
```bash
curl -H "Authorization: Bearer your-mcp-bearer-token-here" \
     -H "Content-Type: application/json" \
     -X POST https://your-project.vercel.app/api \
     -d '{"method": "tools/call", "params": {"name": "list_gitlab_projects", "arguments": {}}}'
```

The GitLab token is configured via environment variables and used automatically for GitLab API calls, so you don't need to pass it when calling tools.

## Optional: Self-Hosted GitLab

If using a self-hosted GitLab instance, set the environment variable in Vercel:

```bash
vercel env add GITLAB_API_URL
# Enter: https://your-gitlab-instance.com/api/v4
```

Or set it in the Vercel dashboard under Project Settings > Environment Variables.

**Note:** You still need to set `GITLAB_PRIVATE_TOKEN` with a token from your self-hosted instance.

