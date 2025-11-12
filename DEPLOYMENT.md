# Deployment Guide

## Vercel Deployment

### Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. GitLab personal access token
3. Vercel CLI (optional, for CLI deployment)

### Deploy via Vercel CLI

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Navigate to project directory:**
   ```bash
   cd "/Users/brainbetechuoh/Desktop/GitLab MCP"
   ```

4. **Deploy:**
   ```bash
   vercel
   ```

5. **Set environment variables:**
   ```bash
   vercel env add GITLAB_TOKEN
   # Enter your GitLab token when prompted
   
   vercel env add GITLAB_BASE_URL
   # Enter: https://gitlab.com/api/v4
   # (or your self-hosted GitLab URL)
   
   vercel env add SERVER_BEARER_TOKEN
   # Enter a secure bearer token (optional but recommended)
   # This token will be required for HTTP endpoint access
   ```

6. **Deploy to production:**
   ```bash
   vercel --prod
   ```

### Deploy via Vercel Dashboard

1. **Push your code to Git:**
   - Create a Git repository (GitHub, GitLab, Bitbucket)
   - Push your code

2. **Import to Vercel:**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your Git repository
   - Vercel will auto-detect Python

3. **Configure environment variables:**
   - Go to Project Settings → Environment Variables
   - Add:
     - `GITLAB_TOKEN`: Your GitLab personal access token
     - `GITLAB_BASE_URL`: `https://gitlab.com/api/v4` (or your instance URL)
     - `SERVER_BEARER_TOKEN`: (Optional) A secure bearer token for HTTP endpoint authentication

4. **Deploy:**
   - Click "Deploy"
   - Wait for deployment to complete

### Verify Deployment

After deployment, test the health endpoint:

**Without bearer token (if SERVER_BEARER_TOKEN is not set):**
```bash
curl https://your-deployment-url.vercel.app/health
```

**With bearer token (if SERVER_BEARER_TOKEN is set):**
```bash
curl -H "Authorization: Bearer your_server_bearer_token" \
  https://your-deployment-url.vercel.app/health
```

You should see a JSON response with server status and available tools. If bearer token authentication is enabled and the token is missing or incorrect, you'll receive a `401 Unauthorized` response.

## Local Development

For local development and MCP client connections:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export GITLAB_TOKEN="your_token_here"
   export GITLAB_BASE_URL="https://gitlab.com/api/v4"
   ```

   Or create a `.env` file (not committed to git):
   ```
   GITLAB_TOKEN=your_token_here
   GITLAB_BASE_URL=https://gitlab.com/api/v4
   ```

3. **Test the server:**
   ```bash
   python server.py
   ```

   The server will start and wait for stdio input (MCP protocol).

## Troubleshooting

### Vercel Deployment Issues

- **Build fails:** Check that `requirements.txt` is in the root directory
- **Import errors:** Ensure all dependencies are listed in `requirements.txt`
- **Environment variables not working:** Make sure they're set in Vercel dashboard and redeploy

### MCP Client Connection Issues

- **Server not found:** Use absolute paths in MCP client configuration
- **Permission denied:** Ensure Python script is executable: `chmod +x server.py`
- **Import errors:** Make sure all dependencies are installed: `pip install -r requirements.txt`

### GitLab API Issues

- **401 Unauthorized:** Check your `GITLAB_TOKEN` is valid and has correct scopes
- **404 Not Found:** Verify `GITLAB_BASE_URL` is correct
- **Rate limiting:** GitLab API has rate limits; implement retry logic if needed

