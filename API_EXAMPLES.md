# GitLab MCP API Examples

Quick reference for using the deployed API.

## Base URL

After deployment, your API will be available at:
```
https://your-project.vercel.app/api
```

## Authentication

The API uses **Bearer Token Authentication**. All requests (except OPTIONS for CORS) require a valid Bearer token in the Authorization header.

### Setting Up Bearer Tokens

Configure allowed bearer tokens using the `API_BEARER_TOKENS` environment variable:

```bash
# Single token
API_BEARER_TOKENS=your-secret-token-here

# Multiple tokens (comma-separated)
API_BEARER_TOKENS=token1,token2,token3
```

**Note**: If `API_BEARER_TOKENS` is not set, the `GITLAB_TOKEN` will be used as the bearer token for backward compatibility.

### Using Bearer Tokens

Include the token in the `Authorization` header:

```
Authorization: Bearer your-token-here
```

## Examples

### 1. Get API Documentation

```bash
# Index endpoint may be public, but including token is recommended
curl -H "Authorization: Bearer your-token-here" https://your-project.vercel.app/api/
```

### 2. Get Current User Info

```bash
curl -H "Authorization: Bearer your-token-here" https://your-project.vercel.app/api/user
```

**Response:**
```json
{
  "id": 12345,
  "username": "your-username",
  "name": "Your Name",
  "email": "your@email.com",
  "avatar_url": "https://...",
  "web_url": "https://gitlab.com/your-username"
}
```

### 3. List Projects

```bash
# List all projects
curl -H "Authorization: Bearer your-token-here" https://your-project.vercel.app/api/projects

# List owned projects only
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/projects?owned=true"

# Search projects
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/projects?search=my-project"

# Limit results
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/projects?limit=10"
```

### 4. Get Specific Project

```bash
# By ID
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/projects?id=12345"

# By path
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/projects?id=group/project-name"
```

### 5. List Issues

```bash
# List all open issues
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/issues?project_id=group/project"

# List closed issues
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/issues?project_id=group/project&state=closed"

# Filter by labels
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/issues?project_id=group/project&labels=bug,urgent"

# Limit results
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/issues?project_id=group/project&limit=5"
```

### 6. Get Specific Issue

```bash
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/issues?project_id=group/project&issue_iid=1"
```

### 7. Create Issue

```bash
curl -X POST https://your-project.vercel.app/api/issues \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "group/project",
    "title": "New Issue Title",
    "description": "Issue description here",
    "labels": "bug,urgent"
  }'
```

**Response:**
```json
{
  "iid": 42,
  "title": "New Issue Title",
  "state": "opened",
  "web_url": "https://gitlab.com/group/project/-/issues/42",
  "message": "Issue created successfully"
}
```

### 8. List Merge Requests

```bash
# List open merge requests
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/merge_requests?project_id=group/project"

# List merged MRs
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/merge_requests?project_id=group/project&state=merged"

# List all MRs
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/merge_requests?project_id=group/project&state=all"
```

### 9. Get Specific Merge Request

```bash
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/merge_requests?project_id=group/project&mr_iid=5"
```

### 10. List Pipelines

```bash
# List all pipelines
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/pipelines?project_id=group/project"

# Filter by status
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/pipelines?project_id=group/project&status=success"

# Available statuses: running, pending, success, failed, canceled, skipped
```

### 11. List Groups

```bash
# List all groups
curl -H "Authorization: Bearer your-token-here" https://your-project.vercel.app/api/groups

# Search groups
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/groups?search=my-group"

# Limit results
curl -H "Authorization: Bearer your-token-here" "https://your-project.vercel.app/api/groups?limit=10"
```

## JavaScript/TypeScript Examples

### Fetch API

```javascript
const API_TOKEN = 'your-token-here';
const BASE_URL = 'https://your-project.vercel.app/api';

// Get user info
const response = await fetch(`${BASE_URL}/user`, {
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`
  }
});
const user = await response.json();
console.log(user);

// List projects
const projects = await fetch(`${BASE_URL}/projects?owned=true`, {
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`
  }
}).then(res => res.json());
console.log(projects);

// Create issue
const newIssue = await fetch(`${BASE_URL}/issues`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    project_id: 'group/project',
    title: 'New Issue',
    description: 'Issue description',
    labels: 'bug,urgent'
  })
}).then(res => res.json());
console.log(newIssue);
```

### Axios

```javascript
import axios from 'axios';

const API_TOKEN = 'your-token-here';

const api = axios.create({
  baseURL: 'https://your-project.vercel.app/api',
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`
  }
});

// Get user
const user = await api.get('/user');
console.log(user.data);

// List issues
const issues = await api.get('/issues', {
  params: {
    project_id: 'group/project',
    state: 'opened'
  }
});
console.log(issues.data);

// Create issue
const newIssue = await api.post('/issues', {
  project_id: 'group/project',
  title: 'New Issue',
  description: 'Description',
  labels: 'bug'
});
console.log(newIssue.data);
```

## Python Examples

```python
import requests

BASE_URL = "https://your-project.vercel.app/api"
API_TOKEN = "your-token-here"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

# Get user info
response = requests.get(f"{BASE_URL}/user", headers=headers)
user = response.json()
print(user)

# List projects
response = requests.get(
    f"{BASE_URL}/projects",
    params={"owned": True},
    headers=headers
)
projects = response.json()
print(projects)

# Create issue
response = requests.post(
    f"{BASE_URL}/issues",
    json={
        "project_id": "group/project",
        "title": "New Issue",
        "description": "Issue description",
        "labels": "bug,urgent"
    },
    headers=headers
)
issue = response.json()
print(issue)
```

## Error Handling

All endpoints return errors in this format:

```json
{
  "error": "Error message here"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created (for POST requests)
- `400` - Bad Request (missing or invalid parameters)
- `401` - Unauthorized (missing or invalid bearer token)
- `405` - Method Not Allowed
- `500` - Internal Server Error

### Authentication Errors

If you receive a `401 Unauthorized` error, check:

1. **Missing Authorization header**: Make sure you're including the `Authorization: Bearer <token>` header
2. **Invalid token**: Verify your token is correct and matches one of the tokens in `API_BEARER_TOKENS`
3. **Token not configured**: Ensure `API_BEARER_TOKENS` is set in your environment variables (or `GITLAB_TOKEN` as fallback)

Example error handling:

```javascript
try {
  const response = await fetch('https://your-project.vercel.app/api/issues?project_id=invalid');
  const data = await response.json();
  
  if (data.error) {
    console.error('Error:', data.error);
  } else {
    console.log('Success:', data);
  }
} catch (error) {
  console.error('Request failed:', error);
}
```

## CORS

CORS is enabled for all origins. You can make requests from any web application.

## Rate Limiting

Be mindful of GitLab API rate limits. The API will return errors if rate limits are exceeded.

