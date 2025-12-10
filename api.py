import os
import json
import asyncio
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import yaml

app = FastAPI(title='Faberlic Satire RAG API', version='1.0')

# Load configuration
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

class ContentRequest(BaseModel):
    platform: str
    topic: str
    style: str = 'satirical_witty'
    language: str = 'en'

class ContentResponse(BaseModel):
    platform: str
    content: str
    hashtags: List[str]
    timestamp: str

@app.get('/health')
async def health_check():
    return {'status': 'healthy', 'version': '1.0'}

@app.get('/config')
async def get_config():
    return {'platforms': list(config['platforms'].keys())}

@app.post('/generate')
async def generate_content(request: ContentRequest) -> ContentResponse:
    '''
    Generate satirical content for Faberlic products
    '''
    if request.platform not in config['platforms']:
        raise HTTPException(status_code=400, detail=f'Unknown platform: {request.platform}')
    
    platform_config = config['platforms'][request.platform]
    if not platform_config['enabled']:
        raise HTTPException(status_code=400, detail=f'Platform {request.platform} is disabled')
    
    # Prepare prompt for LLM
    llm_settings = config['llm_settings']
    content_gen = config['content_generation']
    
    prompt = f"""
    Generate {content_gen['tone']} content about {request.topic} for Faberlic beauty products.
    Target audience: {content_gen['target_audience']}
    Language: {request.language}
    Platform: {request.platform}
    Keep it witty, engaging, and authentic to the product benefits.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model=llm_settings['model'],
            messages=[
                {'role': 'system', 'content': llm_settings['system_prompt']},
                {'role': 'user', 'content': prompt}
            ],
            temperature=llm_settings['temperature'],
            max_tokens=llm_settings['max_tokens']
        )
        
        content = response['choices'][0]['message']['content']
        hashtags = platform_config.get('hashtags', [])
        
        return ContentResponse(
            platform=request.platform,
            content=content,
            hashtags=hashtags,
            timestamp=str(asyncio.get_event_loop().time())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Content generation error: {str(e)}')

@app.get('/platforms')
async def list_platforms():
    return {
        'platforms': [
            {
                'name': name,
                'enabled': config['platforms'][name]['enabled'],
                'schedule': config['platforms'][name]['posting_schedule'],
                'content_type': config['platforms'][name]['content_type']
            }
            for name in config['platforms'].keys()
        ]
    }

@app.post('/batch')
async def batch_generate(requests: List[ContentRequest]):
    '''
    Generate multiple content pieces at once
    '''
    results = []
    for req in requests:
        try:
            result = await generate_content(req)
            results.append(result)
        except HTTPException as e:
            results.append({'error': str(e.detail)})
    return results

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
