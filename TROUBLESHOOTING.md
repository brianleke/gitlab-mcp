# Troubleshooting FUNCTION_INVOCATION_FAILED

If you're getting a `FUNCTION_INVOCATION_FAILED` error after deploying to Vercel, follow these steps:

## 1. Check Vercel Function Logs

The most important step is to check the actual error in Vercel's logs:

1. Go to your Vercel project dashboard
2. Click on the failed deployment
3. Go to the **Functions** tab
4. Click on the specific function that's failing
5. View the **Logs** section

This will show you the actual error message and stack trace.

## 2. Verify Environment Variables

Make sure your environment variables are set correctly:

1. Go to **Project Settings** → **Environment Variables**
2. Verify these are set:
   - `GITLAB_URL` - Your GitLab instance URL (e.g., `https://gitlab.com`)
   - `GITLAB_TOKEN` - Your GitLab Personal Access Token

3. Make sure they're set for the correct environment (Production, Preview, Development)

## 3. Test the API with Error Details

The updated code now includes detailed error messages. Try calling the API:

```bash
curl https://your-project.vercel.app/api/user
```

The response should now include a detailed error message with a traceback if something is wrong.

## 4. Common Issues and Solutions

### Issue: Import Errors

**Symptom**: `ModuleNotFoundError` or `ImportError` in logs

**Solution**: The code now handles imports with fallbacks. If you still see import errors, check:
- All files are in the `api/` directory
- `requirements.txt` includes all dependencies
- The `__init__.py` file exists in the `api/` directory

### Issue: Missing Environment Variables

**Symptom**: `GITLAB_TOKEN environment variable is required`

**Solution**: 
1. Set `GITLAB_TOKEN` in Vercel dashboard
2. Redeploy the function
3. Make sure the token has the `api` scope

### Issue: GitLab Authentication Failed

**Symptom**: `401 Unauthorized` or authentication errors

**Solution**:
1. Verify your GitLab token is valid
2. Check token hasn't expired
3. Ensure token has required scopes (`api`, `read_api`)

### Issue: Request Format Errors

**Symptom**: Errors related to request parsing

**Solution**: The updated code handles different request formats. If issues persist:
- Check Vercel logs for the actual request structure
- The error response will include the traceback

### Issue: Timeout Errors

**Symptom**: Function times out

**Solution**:
- Reduce the `limit` parameter in API calls
- Optimize GitLab API queries
- Consider caching frequently accessed data

## 5. Test Locally

Test the functions locally before deploying:

```bash
# Install Vercel CLI
npm i -g vercel

# Run locally
vercel dev
```

This will help catch issues before deployment.

## 6. Check Dependencies

Verify `requirements.txt` includes:

```
python-gitlab>=4.0.0
```

The MCP package is not needed for the API deployment.

## 7. Verify File Structure

Your project should have this structure:

```
.
├── api/
│   ├── __init__.py
│   ├── gitlab_client.py
│   ├── utils.py
│   ├── index.py
│   ├── user.py
│   ├── projects.py
│   ├── issues.py
│   ├── merge_requests.py
│   ├── pipelines.py
│   └── groups.py
├── vercel.json
├── requirements.txt
└── README.md
```

## 8. Debug Mode

The updated handlers now include full tracebacks in error responses. When you call the API and get an error, the response will include:

```json
{
  "error": "Error message here\n\nTraceback:\n[full stack trace]"
}
```

This will help identify exactly where the error is occurring.

## 9. Check Vercel Build Logs

1. Go to your deployment
2. Click on **Build Logs**
3. Look for any build-time errors or warnings

## 10. Common Python Runtime Issues

### Python Version
Vercel uses Python 3.9 by default. Make sure your code is compatible.

### Missing Dependencies
All dependencies must be in `requirements.txt`. Vercel will install them automatically.

### Path Issues
The updated code handles path issues by adding the current directory to `sys.path`.

## Still Having Issues?

If you've tried all the above:

1. **Check the actual error in Vercel logs** - This is the most important step
2. **Share the error message** - The updated code now provides detailed error messages
3. **Verify your GitLab token** - Test it directly with the GitLab API
4. **Test with a simple endpoint** - Try `/api/` first to see if basic routing works

## Example Debug Request

```bash
# Test the index endpoint (simplest)
curl https://your-project.vercel.app/api/

# Test user endpoint
curl https://your-project.vercel.app/api/user

# If you get an error, the response will include full details
```

The error response will now include the full Python traceback, making it much easier to identify the issue.

