# Vercel Deployment Guide

This guide will help you deploy the GitLab MCP API to Vercel.

## Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. A GitLab Personal Access Token with `api` scope
3. Git repository (GitHub, GitLab, or Bitbucket) with your code

## Deployment Steps

### 1. Prepare Your Repository

Make sure your code is in a Git repository:

```bash
git init
git add .
git commit -m "Initial commit: GitLab MCP API"
git remote add origin <your-repo-url>
git push -u origin main
```

### 2. Deploy to Vercel

#### Option A: Using Vercel CLI

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Set environment variables:
```bash
vercel env add GITLAB_URL
vercel env add GITLAB_TOKEN
```

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)

4. Add Environment Variables:
   - Go to Project Settings → Environment Variables
   - Add the following:
     - `GITLAB_URL`: Your GitLab instance URL (e.g., `https://gitlab.com`)
     - `GITLAB_TOKEN`: Your GitLab Personal Access Token

5. Deploy!

### 3. Environment Variables

Set these in your Vercel project settings:

- **GITLAB_URL**: Your GitLab instance URL
  - Default: `https://gitlab.com`
  - For self-hosted: `https://your-gitlab-instance.com`

- **GITLAB_TOKEN**: Your GitLab Personal Access Token
  - Get one from: https://gitlab.com/-/user_settings/personal_access_tokens
  - Required scopes: `api`, `read_api`

### 4. Verify Deployment

Once deployed, your API will be available at:
```
https://your-project.vercel.app/api/
```

Test the API:
```bash
curl https://your-project.vercel.app/api/
```

## API Endpoints

After deployment, you can access:

- `GET /api/` - API documentation
- `GET /api/user` - Current user info
- `GET /api/projects` - List projects
- `GET /api/projects?id=<project_id>` - Get specific project
- `GET /api/issues?project_id=<project_id>` - List issues
- `GET /api/issues?project_id=<project_id>&issue_iid=<iid>` - Get specific issue
- `POST /api/issues` - Create issue
- `GET /api/merge_requests?project_id=<project_id>` - List merge requests
- `GET /api/pipelines?project_id=<project_id>` - List pipelines
- `GET /api/groups` - List groups

## Example API Calls

### Get User Info
```bash
curl https://your-project.vercel.app/api/user
```

### List Projects
```bash
curl https://your-project.vercel.app/api/projects?owned=true&limit=10
```

### List Issues
```bash
curl "https://your-project.vercel.app/api/issues?project_id=group/project&state=opened"
```

### Create Issue
```bash
curl -X POST https://your-project.vercel.app/api/issues \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "group/project",
    "title": "New Issue",
    "description": "Issue description",
    "labels": "bug,urgent"
  }'
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are in `requirements.txt`
2. **Environment Variables**: Verify they're set in Vercel dashboard
3. **CORS Issues**: CORS is enabled by default, but check browser console for errors
4. **Timeout Errors**: Vercel has execution time limits; optimize your queries

### Debugging

Check Vercel function logs:
1. Go to your project dashboard
2. Click on "Functions" tab
3. View logs for each API endpoint

### Local Testing

You can test locally using Vercel CLI:

```bash
vercel dev
```

This will start a local server that mimics Vercel's environment.

## Security Notes

⚠️ **Important**: 
- Never commit your `GITLAB_TOKEN` to the repository
- Use Vercel's environment variables for sensitive data
- Consider using Vercel's environment variable encryption
- For production, consider adding API authentication/rate limiting

## Custom Domain

To use a custom domain:
1. Go to Project Settings → Domains
2. Add your domain
3. Follow DNS configuration instructions

## Continuous Deployment

Vercel automatically deploys on every push to your main branch. To disable:
1. Go to Project Settings → Git
2. Unlink the repository or disable auto-deploy

## Monitoring

Monitor your API:
- View analytics in Vercel dashboard
- Set up alerts for errors
- Monitor function execution times

## Support

For issues:
- Check Vercel documentation: https://vercel.com/docs
- Check GitLab API docs: https://docs.gitlab.com/ee/api/
- Review function logs in Vercel dashboard

