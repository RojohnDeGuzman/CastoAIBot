# Authentication Status - CASI Backend

## Current Status: TEMPORARILY DISABLED FOR TESTING

Authentication has been temporarily disabled in the backend to allow testing without requiring Microsoft Graph API integration.

## What Was Changed

### In `api/index.py`:

1. **Chat Endpoint (`/chat`)**: Authentication check commented out
2. **Knowledge Endpoints (`/knowledge`)**: Authentication checks commented out  
3. **Added Debug Logging**: Enhanced logging for troubleshooting
4. **Added Test Endpoint**: `/test` endpoint for basic connectivity testing

### Authentication Functions Still Available:

- `get_user_email_from_token()` - Function to extract email from Microsoft Graph API token
- `is_castotravel_user()` - Function to check if email ends with `@castotravel.ph`

## How to Re-enable Authentication

### 1. Uncomment Authentication Checks

In `api/index.py`, find these sections and uncomment them:

```python
# In the chat endpoint:
email = get_user_email_from_token(access_token)
if not email or not is_castotravel_user(email):
    return jsonify({"error": "Unauthorized: Only castotravel.ph users allowed"}), 403

# In the knowledge endpoints:
email = get_user_email_from_token(access_token)
if email != "rojohn.deguzman@castotravel.ph":
    return jsonify({"error": "Unauthorized: Only rojohn.deguzman@castotravel.ph can add knowledge."}), 403
```

### 2. Remove Test Placeholder

Replace this line:
```python
email = "test@example.com"  # Placeholder for testing
```

With:
```python
email = get_user_email_from_token(access_token)
```

### 3. Update Health Check

Change the authentication status back to `True` in the health check endpoint.

## Testing the Backend

### Run the Test Script

```bash
python test_backend.py
```

This will test:
- Health check endpoint (`/`)
- Test endpoint (`/test`) 
- Chat endpoint (`/chat`)
- Knowledge endpoints (`/knowledge`)

### Manual Testing

You can also test manually using curl or any HTTP client:

```bash
# Health check
curl https://casto-ai-bot.vercel.app/

# Test endpoint
curl https://casto-ai-bot.vercel.app/test

# Chat endpoint
curl -X POST https://casto-ai-bot.vercel.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, this is a test"}'
```

## Current Configuration

- **Backend URL**: `https://casto-ai-bot.vercel.app`
- **Authentication**: Disabled (temporary)
- **API Key**: Required (GROQ_API_KEY environment variable)
- **Rate Limiting**: Enabled (60 requests per minute)

## Next Steps

1. **Test the backend** using the test script
2. **Verify functionality** works without authentication
3. **Fix Microsoft Graph API integration** in the frontend
4. **Re-enable authentication** once integration is working
5. **Test with real authentication** tokens

## Troubleshooting

### Common Issues:

1. **GROQ_API_KEY not configured**: Check Vercel environment variables
2. **Rate limiting**: Wait 1 minute between requests
3. **Network issues**: Verify backend URL is accessible

### Debug Information:

The backend now includes enhanced logging. Check Vercel logs for detailed information about requests and responses.

## Security Note

⚠️ **WARNING**: With authentication disabled, the backend is accessible to anyone. This is only for testing purposes. Do not deploy to production with authentication disabled.

Re-enable authentication before deploying to production or sharing the backend URL publicly.
