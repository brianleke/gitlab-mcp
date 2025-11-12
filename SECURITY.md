# Security Guide

## Bearer Token Authentication

The GitLab MCP Server supports bearer token authentication to secure HTTP endpoints (such as those deployed on Vercel).

### How It Works

1. **Set `SERVER_BEARER_TOKEN` environment variable** with a secure token
2. **Clients must include** the token in the `Authorization` header:
   ```
   Authorization: Bearer your_server_bearer_token
   ```
3. **If the token is missing or incorrect**, the server returns `401 Unauthorized`

### Enabling Bearer Token Authentication

#### Local Development

Set the environment variable:
```bash
export SERVER_BEARER_TOKEN="your_secure_token_here"
```

Or in your `.env` file:
```
SERVER_BEARER_TOKEN=your_secure_token_here
```

#### Vercel Deployment

Add the environment variable in Vercel:
```bash
vercel env add SERVER_BEARER_TOKEN
```

Or via the Vercel dashboard:
1. Go to Project Settings → Environment Variables
2. Add `SERVER_BEARER_TOKEN` with your secure token
3. Redeploy

### Generating a Secure Token

Generate a secure random token:

**Using Python:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

**Using OpenSSL:**
```bash
openssl rand -hex 32
```

**Using Node.js:**
```javascript
require('crypto').randomBytes(32).toString('hex')
```

### Using Bearer Token in Requests

**cURL:**
```bash
curl -H "Authorization: Bearer your_token" \
  https://your-server-url.vercel.app/health
```

**Python:**
```python
import requests

headers = {
    "Authorization": "Bearer your_token"
}
response = requests.get("https://your-server-url.vercel.app/health", headers=headers)
```

**JavaScript/Node.js:**
```javascript
fetch('https://your-server-url.vercel.app/health', {
  headers: {
    'Authorization': 'Bearer your_token'
  }
})
```

### Disabling Bearer Token Authentication

To disable bearer token authentication (not recommended for production):
- Leave `SERVER_BEARER_TOKEN` unset or empty
- The server will allow access without authentication

**Warning:** Only disable bearer token authentication in development or if the server is behind additional security layers (e.g., VPN, firewall, API gateway).

### Security Best Practices

1. **Use strong, random tokens** - Generate tokens using cryptographically secure random generators
2. **Store tokens securely** - Never commit tokens to version control
3. **Use HTTPS** - Always use HTTPS in production to protect tokens in transit
4. **Rotate tokens regularly** - Change tokens periodically, especially if compromised
5. **Limit token scope** - Use different tokens for different environments (dev, staging, production)
6. **Monitor access** - Log and monitor authentication attempts
7. **Use environment variables** - Store tokens in environment variables, not in code

### Token Storage

**Do:**
- ✅ Store in environment variables
- ✅ Use secret management services (AWS Secrets Manager, HashiCorp Vault, etc.)
- ✅ Use `.env` files (and ensure they're in `.gitignore`)

**Don't:**
- ❌ Commit tokens to Git
- ❌ Hardcode tokens in source code
- ❌ Share tokens in plain text (use secure channels)
- ❌ Use weak or predictable tokens

### Troubleshooting

**401 Unauthorized:**
- Check that `SERVER_BEARER_TOKEN` is set correctly
- Verify the token in the `Authorization` header matches exactly
- Ensure the header format is: `Authorization: Bearer <token>` (with a space after "Bearer")

**Token not working after deployment:**
- Ensure environment variables are set in Vercel
- Redeploy after setting environment variables
- Check that the token doesn't have extra spaces or newlines

