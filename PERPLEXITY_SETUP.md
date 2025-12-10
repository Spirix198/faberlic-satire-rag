# Perplexity Pro API Integration Setup

## Overview

This project has been migrated from OpenAI API to **Perplexity Pro API** for improved Russian-language satirical content generation and cost efficiency.

## Quick Start

### 1. Get Your Perplexity API Key

1. Visit [Perplexity AI Settings](https://www.perplexity.ai/settings/api)
2. Sign in or create an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you'll only see it once!)

### 2. Configure Environment Variables

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your Perplexity API key
# PERPLEXITY_API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API

```bash
python api.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Generate Content
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "telegram",
    "topic": "Minimalism trends",
    "style": "satirical_witty",
    "language": "ru",
    "use_search": false
  }'
```

### Batch Generation
```bash
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '[...array of requests...]'
```

## Security Best Practices

### CRITICAL: API Key Management

⚠️ **NEVER commit your .env file to version control!**

✅ **DO:**
- Store API key in `.env` file (NOT committed)
- Use environment variables in production
- Rotate keys regularly
- Monitor API usage for suspicious activity
- Use secrets manager (AWS Secrets Manager, HashiCorp Vault)

❌ **DON'T:**
- Commit `.env` to git
- Share API key via email or chat
- Log API key in error messages
- Use same key across environments
- Hardcode credentials in code

### Checking .gitignore

Verify `.env` is in `.gitignore`:

```bash
cat .gitignore | grep -E '^.env$'
```

Should output:
```
.env
```

## API Models Available

### pplx-70b-online (Default)
- Uses real-time web search
- Better for current event references
- Slight latency increase
- Recommended for news/trending topics

### pplx-70b-chat
- Offline, trained knowledge only
- Faster response times
- Good for general creative content

Change model in `.env`:
```
PERPLEXITY_MODEL=pplx-70b-chat
```

## Troubleshooting

### "API key not configured" error
```bash
# Verify PERPLEXITY_API_KEY is set
echo $PERPLEXITY_API_KEY

# Or check .env file exists and has the key
cat .env | grep PERPLEXITY_API_KEY
```

### Connection timeout
- Check internet connection
- Verify API endpoint: `https://api.perplexity.ai/chat/completions`
- Check if your IP is blocked/rate-limited

### Rate limiting
- Default limit: 60 requests/minute
- Configure in `.env`: `MAX_REQUESTS_PER_MINUTE=60`
- Implement request queuing for batch jobs

## Environment Variables Reference

```env
# REQUIRED
PERPLEXITY_API_KEY=your_key_here

# OPTIONAL
PERPLEXITY_API_URL=https://api.perplexity.ai/chat/completions
PERPLEXITY_MODEL=pplx-70b-online
ENVIRONMENT=development
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
REQUEST_TIMEOUT=30
MAX_REQUESTS_PER_MINUTE=60
```

## Production Deployment

### Docker
```bash
docker build -t faberlic-satire-rag .
docker run -e PERPLEXITY_API_KEY=$KEY -p 8000:8000 faberlic-satire-rag
```

### Using Secrets Manager

**AWS Secrets Manager:**
```python
import boto3
secrets_client = boto3.client('secretsmanager')
secret = secrets_client.get_secret_value(SecretId='perplexity-api-key')
api_key = secret['SecretString']
```

**HashiCorp Vault:**
```python
import hvac
client = hvac.Client(url='https://vault.example.com')
secret = client.secrets.kv.read_secret_version('secret/perplexity')
api_key = secret['data']['data']['PERPLEXITY_API_KEY']
```

## Monitoring

### Log API Requests
Check logs for API usage:
```bash
# Local development
tail -f api.log | grep PERPLEXITY

# Production (with structured logging)
jq 'select(.service=="api" and .component=="perplexity")' logs.json
```

### Check API Balance
Monitor your Perplexity API dashboard for:
- Token usage
- Request count
- Error rates
- Cost tracking

## Migration from OpenAI

If you were using OpenAI before:

**Old (OpenAI):**
```python
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = client.chat.completions.create(...)
```

**New (Perplexity):**
```python
import httpx
async with httpx.AsyncClient() as client:
    response = await client.post(
        'https://api.perplexity.ai/chat/completions',
        headers={'Authorization': f'Bearer {PERPLEXITY_API_KEY}'},
        json={...}
    )
```

## Support

For issues:
1. Check [Perplexity API Documentation](https://docs.perplexity.ai/)
2. Review logs with `LOG_LEVEL=DEBUG`
3. Test endpoint: `curl -v https://api.perplexity.ai/`
4. Contact Perplexity support with your API key issues

## License

This integration follows MIT License. API key security is YOUR responsibility.
