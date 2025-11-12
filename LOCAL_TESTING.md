# Local Testing Guide

This guide will help you run and test the GitLab MCP API locally before deploying to Vercel.

## Prerequisites

1. **Python 3.8+** installed
2. **Vercel CLI** installed (for local Vercel environment)
3. **GitLab Personal Access Token** ready

## Method 1: Using Vercel CLI (Recommended)

This method simulates the Vercel environment locally.

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

### Step 3: Set Up Environment Variables

Create a `.env` file in the project root (or use `env.example` as a template):

```bash
cp env.example .env
```

Edit `.env` and add your GitLab credentials:
```
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=your_personal_access_token_here
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run Locally

```bash
vercel dev
```

This will:
- Start a local server (usually at `http://localhost:3000`)
- Simulate the Vercel environment
- Use your `.env` file for environment variables

### Step 6: Test the API

Once the server is running, test the endpoints:

```bash
# Test the index endpoint
curl http://localhost:3000/api/

# Test user endpoint
curl http://localhost:3000/api/user

# Test projects endpoint
curl http://localhost:3000/api/projects?owned=true&limit=5
```

## Method 2: Direct Python Testing

You can also test the handlers directly using Python's HTTP server.

### Step 1: Create a Test Server Script

Create `test_server.py`:

```python
#!/usr/bin/env python3
"""
Simple test server for local development.
"""

import os
import sys
from http.server import HTTPServer
from api.index import handler as index_handler
from api.user import handler as user_handler
from api.projects import handler as projects_handler

# Set environment variables
os.environ.setdefault('GITLAB_URL', 'https://gitlab.com')
os.environ.setdefault('GITLAB_TOKEN', 'your_token_here')  # Replace with your token

class RequestHandler:
    def __init__(self, handler_class):
        self.handler_class = handler_class
    
    def __call__(self, *args, **kwargs):
        return self.handler_class(*args, **kwargs)

def run_server(port=8000):
    server_address = ('', port)
    
    # Simple routing
    class Router:
        def __init__(self):
            self.routes = {
                '/api/': index_handler,
                '/api/user': user_handler,
                '/api/projects': projects_handler,
            }
        
        def get_handler(self, path):
            # Remove query string
            path = path.split('?')[0]
            return self.routes.get(path, index_handler)
    
    router = Router()
    
    class CustomHandler:
        def __init__(self, request, client_address, server):
            self.request = request
            self.client_address = client_address
            self.server = server
            self.path = request.path
            self.headers = {}
            self.rfile = request.makefile('rb', -1)
            self.wfile = request.makefile('wb', 0)
            
            handler_class = router.get_handler(self.path)
            self.handler = handler_class(self, client_address, server)
            
            # Parse headers
            line = self.rfile.readline()
            while line and line.strip():
                if b':' in line:
                    key, value = line.split(b':', 1)
                    self.headers[key.decode().lower()] = value.decode().strip()
                line = self.rfile.readline()
            
            # Handle request
            method = self.request.command
            if method == 'GET':
                self.handler.do_GET()
            elif method == 'POST':
                self.handler.do_POST()
            elif method == 'OPTIONS':
                self.handler.do_OPTIONS()
    
    httpd = HTTPServer(server_address, CustomHandler)
    print(f'Server running on http://localhost:{port}/')
    print('Press Ctrl+C to stop')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
```

### Step 2: Run the Test Server

```bash
python test_server.py
```

## Method 3: Using Python's http.server (Simplest)

For quick testing, you can use a simple wrapper:

### Create `local_test.py`:

```python
#!/usr/bin/env python3
"""
Quick local test script.
"""

import os
import sys
import json
from urllib.parse import urlparse, parse_qs

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

# Set environment variables
os.environ['GITLAB_URL'] = 'https://gitlab.com'
os.environ['GITLAB_TOKEN'] = 'your_token_here'  # Replace with your token

# Import handlers
from index import handler as index_handler
from user import handler as user_handler

# Create a mock request handler
class MockRequest:
    def __init__(self, path='/api/', method='GET'):
        self.path = path
        self.command = method
        self.headers = {}
        self.rfile = None
        self.wfile = None

# Test index
print("Testing /api/ endpoint...")
mock = MockRequest('/api/', 'GET')
index_handler(mock, ('127.0.0.1', 8000), None)
```

## Quick Test Script

Create `test_api.sh`:

```bash
#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:3000"

echo "Testing GitLab MCP API..."
echo ""

# Test 1: Index endpoint
echo -e "${GREEN}Test 1: GET /api/${NC}"
curl -s "$BASE_URL/api/" | jq '.' || echo "Failed"
echo ""

# Test 2: User endpoint
echo -e "${GREEN}Test 2: GET /api/user${NC}"
curl -s "$BASE_URL/api/user" | jq '.' || echo "Failed"
echo ""

# Test 3: Projects endpoint
echo -e "${GREEN}Test 3: GET /api/projects?owned=true&limit=3${NC}"
curl -s "$BASE_URL/api/projects?owned=true&limit=3" | jq '.' || echo "Failed"
echo ""

# Test 4: Groups endpoint
echo -e "${GREEN}Test 4: GET /api/groups?limit=3${NC}"
curl -s "$BASE_URL/api/groups?limit=3" | jq '.' || echo "Failed"
echo ""

echo "Testing complete!"
```

Make it executable:
```bash
chmod +x test_api.sh
```

Run it:
```bash
./test_api.sh
```

## Testing Individual Endpoints

### Using curl

```bash
# Index (API documentation)
curl http://localhost:3000/api/

# User info
curl http://localhost:3000/api/user

# List projects
curl "http://localhost:3000/api/projects?owned=true&limit=5"

# Get specific project
curl "http://localhost:3000/api/projects?id=your-project-id"

# List issues
curl "http://localhost:3000/api/issues?project_id=group/project&state=opened"

# List merge requests
curl "http://localhost:3000/api/merge_requests?project_id=group/project"

# List pipelines
curl "http://localhost:3000/api/pipelines?project_id=group/project"

# List groups
curl "http://localhost:3000/api/groups?limit=10"
```

### Using Python requests

Create `test_requests.py`:

```python
#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:3000"

def test_endpoint(path, params=None):
    """Test an API endpoint."""
    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url, params=params)
        print(f"\n{path}:")
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test endpoints
test_endpoint("/api/")
test_endpoint("/api/user")
test_endpoint("/api/projects", {"owned": "true", "limit": "3"})
test_endpoint("/api/groups", {"limit": "3"})
```

Run it:
```bash
pip install requests
python test_requests.py
```

### Using httpie (if installed)

```bash
# Install httpie
pip install httpie

# Test endpoints
http GET localhost:3000/api/
http GET localhost:3000/api/user
http GET localhost:3000/api/projects owned==true limit==5
```

## Environment Variables

Make sure your `.env` file contains:

```bash
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=glpat-your-token-here
```

Or set them in your shell:

```bash
export GITLAB_URL=https://gitlab.com
export GITLAB_TOKEN=your_token_here
```

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Make sure you're in the project root directory and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "GITLAB_TOKEN environment variable is required"

**Solution**: Make sure your `.env` file exists and contains the token, or set it as an environment variable.

### Issue: Port already in use

**Solution**: Vercel CLI will automatically find an available port. Or specify a different port:
```bash
vercel dev --listen 3001
```

### Issue: Import errors

**Solution**: The imports should work automatically with Vercel CLI. If testing directly with Python, make sure the `api` directory is in your Python path.

## Debugging Tips

1. **Check Vercel logs**: When running `vercel dev`, check the terminal for error messages
2. **Add print statements**: Add `print()` statements in your handlers to debug
3. **Test with curl**: Use `curl -v` for verbose output to see headers and responses
4. **Check environment variables**: Print them at the start of your handler to verify they're set

## Example: Full Test Workflow

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp env.example .env
# Edit .env with your token

# 3. Start local server
vercel dev

# 4. In another terminal, test endpoints
curl http://localhost:3000/api/user

# 5. Test with a real project
curl "http://localhost:3000/api/issues?project_id=your-group/your-project"
```

## Next Steps

Once local testing works:
1. Commit your changes
2. Push to your Git repository
3. Deploy to Vercel
4. Test the deployed endpoints

The local environment should match the production Vercel environment closely!

