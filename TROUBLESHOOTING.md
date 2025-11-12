# Troubleshooting Vercel Deployment

## Error: "Python process exited with exit status: 1"

This error indicates the Python process is crashing before it can return a response. Here's how to debug:

### Step 1: Check Vercel Logs

1. Go to your Vercel Dashboard
2. Select your project
3. Click on "Deployments"
4. Click on the latest deployment
5. Click on "Logs" or "Function Logs"
6. Look for the specific error message

The logs will show the actual Python error that's causing the crash.

### Step 2: Test with Minimal Handler

Try deploying with the ultra-minimal handler in `api/health.py`:

1. Update `vercel.json` to use `api/health.py`:
```json
{
  "builds": [{"src": "api/health.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "api/health.py"}]
}
```

2. Deploy and test `/health`

If this works, the issue is in the main handler. If it doesn't, there's a Vercel configuration issue.

### Step 3: Common Issues

#### Issue: Missing Dependencies
**Symptom**: Import errors in logs
**Solution**: Ensure all dependencies are in `requirements.txt`

#### Issue: Syntax Error
**Symptom**: Syntax errors in logs
**Solution**: Run `python -m py_compile api/index.py` locally to check

#### Issue: Handler Signature Wrong
**Symptom**: Handler not being called
**Solution**: Ensure function is named `handler` and takes one parameter

#### Issue: Environment Variables
**Symptom**: Crashes when accessing env vars
**Solution**: Set all required env vars in Vercel dashboard

### Step 4: Local Testing

Test the handler locally:

```python
# test_handler.py
from api.index import handler

# Test request
request = {
    'method': 'GET',
    'path': '/health',
    'headers': {}
}

result = handler(request)
print(result)
```

Run: `python test_handler.py`

### Step 5: Check Python Version

Ensure your local Python version matches Vercel's:
- Vercel uses Python 3.11 by default (as set in vercel.json)
- Test locally with: `python3.11 api/index.py` (if available)

### Step 6: Simplify Handler

If the full handler doesn't work, start with this minimal version:

```python
import json

def handler(request):
    try:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'ok'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
```

### Getting Help

If none of these work:
1. Check Vercel's Python documentation
2. Post in Vercel community forums with:
   - Your handler code
   - Error logs from Vercel
   - Your vercel.json configuration
   - Your requirements.txt

