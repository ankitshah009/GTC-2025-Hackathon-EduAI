from config.settings import Settings
from app.nvidia_api.image_client import NvidiaImageClient
from typing import Dict, List, Any
import asyncio
import time
import random
import hashlib

class ImageService:
    """Service for educational image generation"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.image_client = NvidiaImageClient(settings)
        
    async def generate_image(self, prompt: str) -> str:
        """
        Generate an image based on a text prompt.
        
        Args:
            prompt: Text prompt for image generation
            
        Returns:
            URL to the generated image
        """
        if self.settings.USE_MOCK_DATA:
            # For development/demo, return a placeholder image
            return self._generate_mock_image(prompt)
        
        # Enhance the prompt for educational context
        enhanced_prompt = self._enhance_prompt(prompt)
        
        # Call NVIDIA's text-to-image API
        image_url = await self.image_client.generate_image(enhanced_prompt)
        
        return image_url
    
    def _enhance_prompt(self, prompt: str) -> str:
        """
        Enhance the prompt to improve image generation quality for educational content.
        
        Args:
            prompt: Original text prompt
            
        Returns:
            Enhanced prompt
        """
        # Add educational context and quality parameters
        enhanced_prompt = f"Educational illustration: {prompt}. Clear, detailed, accurate, labeled, professional quality, educational diagram"
        
        return enhanced_prompt
    
    def _generate_mock_image(self, prompt: str) -> str:
        """
        Generate a mock image URL for development and testing.
        
        Args:
            prompt: Text prompt
            
        Returns:
            Placeholder image URL
        """
        # Create a deterministic but random-looking hash from the prompt
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
        
        # Use a placeholder service with the prompt hash for variety
        width = 600
        height = 400
        placeholder_url = f"https://via.placeholder.com/{width}x{height}?text={prompt_hash}"
        
        return placeholder_url
