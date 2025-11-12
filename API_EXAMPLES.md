# GitLab MCP API Examples

Quick reference for using the deployed API.

## Base URL

After deployment, your API will be available at:
```
https://your-project.vercel.app/api
```

## Authentication

The API uses server-side authentication via the `GITLAB_TOKEN` environment variable. No authentication headers are required in API requests.

## Examples

### 1. Get API Documentation

```bash
curl https://your-project.vercel.app/api/
```

### 2. Get Current User Info

```bash
curl https://your-project.vercel.app/api/user
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
curl https://your-project.vercel.app/api/projects

# List owned projects only
curl "https://your-project.vercel.app/api/projects?owned=true"

# Search projects
curl "https://your-project.vercel.app/api/projects?search=my-project"

# Limit results
curl "https://your-project.vercel.app/api/projects?limit=10"
```

### 4. Get Specific Project

```bash
# By ID
curl "https://your-project.vercel.app/api/projects?id=12345"

# By path
curl "https://your-project.vercel.app/api/projects?id=group/project-name"
```

### 5. List Issues

```bash
# List all open issues
curl "https://your-project.vercel.app/api/issues?project_id=group/project"

# List closed issues
curl "https://your-project.vercel.app/api/issues?project_id=group/project&state=closed"

# Filter by labels
curl "https://your-project.vercel.app/api/issues?project_id=group/project&labels=bug,urgent"

# Limit results
curl "https://your-project.vercel.app/api/issues?project_id=group/project&limit=5"
```

### 6. Get Specific Issue

```bash
curl "https://your-project.vercel.app/api/issues?project_id=group/project&issue_iid=1"
```

### 7. Create Issue

```bash
curl -X POST https://your-project.vercel.app/api/issues \
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
curl "https://your-project.vercel.app/api/merge_requests?project_id=group/project"

# List merged MRs
curl "https://your-project.vercel.app/api/merge_requests?project_id=group/project&state=merged"

# List all MRs
curl "https://your-project.vercel.app/api/merge_requests?project_id=group/project&state=all"
```

### 9. Get Specific Merge Request

```bash
curl "https://your-project.vercel.app/api/merge_requests?project_id=group/project&mr_iid=5"
```

### 10. List Pipelines

```bash
# List all pipelines
curl "https://your-project.vercel.app/api/pipelines?project_id=group/project"

# Filter by status
curl "https://your-project.vercel.app/api/pipelines?project_id=group/project&status=success"

# Available statuses: running, pending, success, failed, canceled, skipped
```

### 11. List Groups

```bash
# List all groups
curl https://your-project.vercel.app/api/groups

# Search groups
curl "https://your-project.vercel.app/api/groups?search=my-group"

# Limit results
curl "https://your-project.vercel.app/api/groups?limit=10"
```

## JavaScript/TypeScript Examples

### Fetch API

```javascript
// Get user info
const response = await fetch('https://your-project.vercel.app/api/user');
const user = await response.json();
console.log(user);

// List projects
const projects = await fetch('https://your-project.vercel.app/api/projects?owned=true')
  .then(res => res.json());
console.log(projects);

// Create issue
const newIssue = await fetch('https://your-project.vercel.app/api/issues', {
  method: 'POST',
  headers: {
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

const api = axios.create({
  baseURL: 'https://your-project.vercel.app/api'
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

# Get user info
response = requests.get(f"{BASE_URL}/user")
user = response.json()
print(user)

# List projects
response = requests.get(f"{BASE_URL}/projects", params={"owned": True})
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
    }
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
- `405` - Method Not Allowed
- `500` - Internal Server Error

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

