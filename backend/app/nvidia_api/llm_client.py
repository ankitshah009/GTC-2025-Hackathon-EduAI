import aiohttp
import json
from typing import Dict, Any, List, AsyncGenerator
from config.settings import Settings
from openai import OpenAI, AsyncOpenAI
import asyncio

class LLMClient:
    """Client for LLM API endpoints (using OpenAI SDK)"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_type = settings.LLM_API_TYPE
        self.client = OpenAI(
            base_url=settings.LLM_API_BASE_URL,
            api_key=settings.LLM_API_KEY
        )
        self.async_client = AsyncOpenAI(
            base_url=settings.LLM_API_BASE_URL,
            api_key=settings.LLM_API_KEY
        )
        self.model_id = settings.LLM_MODEL_ID
    
    async def generate_text(self, prompt: str) -> str:
        """
        Generate text using LLM API.
        
        Args:
            prompt: Text prompt for the LLM
            
        Returns:
            Generated text response
        """
        # If using mock data, don't call the API
        if self.settings.USE_MOCK_DATA:
            raise Exception("API should not be called in mock mode")
        
        return await self._generate_text_openai(prompt)
    
    async def _generate_text_openai(self, prompt: str) -> str:
        """Generate text using OpenAI API"""
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": self.settings.LLM_SYSTEM_MESSAGE},
                {"role": "user", "content": prompt}
            ]
            
            # Call OpenAI API
            completion = await self.async_client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=self.settings.LLM_TEMPERATURE,
                top_p=self.settings.LLM_TOP_P,
                max_tokens=self.settings.LLM_MAX_TOKENS,
                frequency_penalty=self.settings.LLM_FREQUENCY_PENALTY,
                presence_penalty=self.settings.LLM_PRESENCE_PENALTY,
                stream=False  # Set to False for regular responses
            )
            
            # Extract generated text
            generated_text = completion.choices[0].message.content
            return generated_text
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def generate_text_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Generate text using LLM API with streaming responses.
        
        Args:
            prompt: Text prompt for the LLM
            
        Yields:
            Chunks of generated text
        """
        # If using mock data, don't call the API
        if self.settings.USE_MOCK_DATA:
            raise Exception("API should not be called in mock mode")
        
        # Prepare messages
        messages = [
            {"role": "system", "content": self.settings.LLM_SYSTEM_MESSAGE},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Call OpenAI API with streaming
            stream = await self.async_client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=self.settings.LLM_TEMPERATURE,
                top_p=self.settings.LLM_TOP_P,
                max_tokens=self.settings.LLM_MAX_TOKENS,
                frequency_penalty=self.settings.LLM_FREQUENCY_PENALTY,
                presence_penalty=self.settings.LLM_PRESENCE_PENALTY,
                stream=True
            )
            
            # Yield chunks of text as they arrive
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise Exception(f"OpenAI API streaming error: {str(e)}")
