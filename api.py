import os
import json
import asyncio
import logging
from typing import Optional, List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import yaml

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title='Faberlic Satire RAG API', version='2.0')

# Load configuration
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Perplexity Pro API Configuration
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

if not PERPLEXITY_API_KEY:
    logger.warning(
        "PERPLEXITY_API_KEY not found in environment variables. "
        "Please set it in .env file or as environment variable."
    )


class ContentRequest(BaseModel):
    """Request model for content generation"""
    platform: str
    topic: str
    style: str = 'satirical_witty'
    language: str = 'ru'
    use_search: bool = False  # Use Perplexity's web search


class ContentResponse(BaseModel):
    """Response model for generated content"""
    platform: str
    content: str
    hashtags: List[str]
    timestamp: str
    model: str = 'pplx-70b-online'


@app.get('/health')
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'version': '2.0',
        'llm_provider': 'Perplexity Pro',
        'api_configured': bool(PERPLEXITY_API_KEY)
    }


@app.get('/config')
async def get_config():
    """Get available platforms configuration"""
    return {'platforms': list(config['platforms'].keys())}


@app.post('/generate')
async def generate_content(request: ContentRequest) -> ContentResponse:
    """
    Generate satirical content using Perplexity Pro API
    
    Perplexity Pro provides:
    - Higher quality responses than standard LLMs
    - Optional web search for up-to-date information
    - Better understanding of nuanced Russian satirical writing
    """
    
    # Validate platform
    if request.platform not in config['platforms']:
        raise HTTPException(
            status_code=400,
            detail=f'Unknown platform: {request.platform}'
        )
    
    platform_config = config['platforms'][request.platform]
    if not platform_config['enabled']:
        raise HTTPException(
            status_code=400,
            detail=f'Platform {request.platform} is disabled'
        )
    
    # Check API key availability
    if not PERPLEXITY_API_KEY:
        raise HTTPException(
            status_code=500,
            detail='Perplexity API key not configured. Please set PERPLEXITY_API_KEY environment variable.'
        )
    
    content_gen = config['content_generation']
    
    # Construct the prompt with Russian-specific satirical style
    system_prompt = f"""
    Ты профессиональный сатирический писатель, специализирующийся на русском юморе в стиле Задорнова и Жванецкого.
    
    Твоя задача: создавать остроумные, провокационные, но доступные сатирические тексты о современных lifestyle трендах.
    
    Стиль: {content_gen['tone']}
    Целевая аудитория: {content_gen['target_audience']}
    Язык: {request.language}
    Платформа: {request.platform}
    
    Требования:
    - Текст должен быть остроумным и провокационным, но не оскорбительным
    - Используй современные примеры и культурные ссылки
    - Сохраняй баланс между критикой и юмором
    - Текст должен быть подходящим для публикации на {request.platform}
    """
    
    user_message = f"""
    Напиши сатирическую статью о: {request.topic}
    
    Длина: 800-1200 слов
    Стиль: {request.style}
    
    Убедись, что текст:
    1. Содержит острый социальный комментарий
    2. Использует иронию и парадокс
    3. Релевантен для целевой аудитории на {request.platform}
    4. Может привлечь интерес к продуктам Faberlic (косметика и ухоз за собой)
    """
    
    try:
        logger.info(f"Generating content for {request.platform} on topic: {request.topic}")
        
        # Prepare request to Perplexity Pro API
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "pplx-70b-online" if request.use_search else "pplx-70b-chat",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "temperature": 0.8,  # Higher temperature for more creative satire
            "top_p": 0.9,
            "max_tokens": 2000,
            "presence_penalty": 0.6  # Encourage diversity in word usage
        }
        
        # Make async request to Perplexity API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                PERPLEXITY_API_URL,
                headers=headers,
                json=payload
            )
        
        if response.status_code != 200:
            error_detail = f"Perplexity API error: {response.status_code}"
            try:
                error_data = response.json()
                error_detail += f" - {error_data.get('error', {}).get('message', 'Unknown error')}"
            except:
                pass
            logger.error(error_detail)
            raise HTTPException(status_code=500, detail=error_detail)
        
        response_data = response.json()
        content = response_data['choices'][0]['message']['content']
        model_used = response_data.get('model', 'pplx-70b-online')
        
        # Get hashtags from platform config
        hashtags = platform_config.get('hashtags', [])
        
        logger.info(f"Successfully generated content for {request.platform}")
        
        return ContentResponse(
            platform=request.platform,
            content=content,
            hashtags=hashtags,
            timestamp=str(asyncio.get_event_loop().time()),
            model=model_used
        )
        
    except httpx.RequestError as e:
        logger.error(f"HTTP request error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f'Failed to reach Perplexity API: {str(e)}'
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during content generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f'Content generation error: {str(e)}'
        )


@app.get('/platforms')
async def list_platforms():
    """List all available platforms"""
    return {
        'platforms': [
            {
                'name': name,
                'enabled': config['platforms'][name]['enabled'],
                'schedule': config['platforms'][name]['posting_schedule'],
                'content_type': config['platforms'][name]['content_type']
            }
            for name in config['platforms'].keys()
        ],
        'llm_provider': 'Perplexity Pro'
    }


@app.post('/batch')
async def batch_generate(requests: List[ContentRequest]):
    """
    Generate multiple content pieces at once
    
    Note: Requests are processed sequentially to avoid rate limiting
    """
    results = []
    for idx, req in enumerate(requests):
        try:
            logger.info(f"Processing batch request {idx + 1}/{len(requests)}")
            result = await generate_content(req)
            results.append(result)
        except HTTPException as e:
            logger.error(f"Error in batch request {idx + 1}: {e.detail}")
            results.append({'error': str(e.detail)})
        except Exception as e:
            logger.error(f"Unexpected error in batch request {idx + 1}: {str(e)}")
            results.append({'error': f'Unexpected error: {str(e)}'})
    
    return results


if __name__ == '__main__':
    import uvicorn
    
    # Warn if API key is not set
    if not PERPLEXITY_API_KEY:
        logger.error(
            "CRITICAL: PERPLEXITY_API_KEY environment variable is not set. "
            "The API will not be able to generate content. "
            "Please set the variable before running the application."
        )
    
    uvicorn.run(app, host='0.0.0.0', port=8000)
