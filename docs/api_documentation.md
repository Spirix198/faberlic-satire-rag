# Faberlic Satire RAG API Documentation

Comprehensive API reference for the Faberlic Satire RAG system with satirical content generation capabilities.

## Base URL

```
https://api.faberlic-satire-rag.com/v1
```

## Authentication

All API requests require an API key passed via the `Authorization` header:

```
Authorization: Bearer YOUR_API_KEY
```

## Rate Limiting

API requests are rate-limited to:
- **30 requests/minute** for standard users
- **300 requests/minute** for premium users  
- **10,000 requests/minute** for enterprise users

Rate limit status is included in response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## Endpoints

### 1. Health Check

**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-10T21:00:00Z",
  "version": "1.0.0"
}
```

### 2. Generate Satirical Content

**POST** `/api/generate`

Generate satirical content based on input parameters.

**Request:**
```json
{
  "prompt": "A humorous take on modern technology",
  "style": "zadornov",
  "length": "medium",
  "tone": "witty",
  "language": "ru"
}
```

**Parameters:**
- `prompt` (string, required): Content generation prompt
- `style` (string): Comedians style (zadornov, zhvanetskiy, dudarkin)
- `length` (string): Content length (short, medium, long)
- `tone` (string): Content tone (witty, sarcastic, absurd)
- `language` (string): Output language (ru, en)

**Response:**
```json
{
  "id": "gen_abc123xyz",
  "content": "Generated satirical text...",
  "style": "zadornov",
  "tokens_used": 256,
  "generated_at": "2024-12-10T21:00:00Z"
}
```

### 3. Analyze Content

**POST** `/api/analyze`

Analyze content for sentiment and satire intensity.

**Request:**
```json
{
  "text": "Some text to analyze",
  "metrics": ["sentiment", "satire_level", "humor_score"]
}
```

**Response:**
```json
{
  "sentiment": {
    "label": "positive",
    "score": 0.89
  },
  "satire_level": 0.92,
  "humor_score": 0.87,
  "analyzed_at": "2024-12-10T21:00:00Z"
}
```

## Error Handling

Errors follow standard HTTP status codes:

- **400 Bad Request**: Invalid parameters
- **401 Unauthorized**: Missing or invalid API key
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

**Error Response:**
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required parameter: prompt",
    "timestamp": "2024-12-10T21:00:00Z"
  }
}
```

## Response Headers

All API responses include:

```
Content-Type: application/json
X-Request-ID: unique-request-identifier
X-Response-Time: milliseconds
Cache-Control: private, max-age=300
```

## Pagination

List endpoints support pagination:

```
GET /api/contents?page=1&limit=20&sort=created_at:desc
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)
- `sort` (string): Sort field and direction

## Webhooks

Configure webhooks for async events:

**POST** `/api/webhooks`

```json
{
  "url": "https://your-domain.com/webhook",
  "events": ["generation_complete", "analysis_complete"],
  "active": true
}
```

## SDK Examples

### Python

```python
import requests

api_key = "your_api_key"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.post(
    "https://api.faberlic-satire-rag.com/v1/api/generate",
    headers=headers,
    json={
        "prompt": "Technology humor",
        "style": "zadornov"
    }
)

result = response.json()
print(result["content"])
```

### JavaScript

```javascript
const apiKey = "your_api_key";

const response = await fetch(
  "https://api.faberlic-satire-rag.com/v1/api/generate",
  {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      prompt: "Technology humor",
      style: "zadornov"
    })
  }
);

const result = await response.json();
console.log(result.content);
```

## Changelog

### v1.0.0 (December 2024)
- Initial API release
- Support for satirical content generation
- Multiple comedian styles
- Rate limiting and authentication
- OpenAPI/Swagger documentation
