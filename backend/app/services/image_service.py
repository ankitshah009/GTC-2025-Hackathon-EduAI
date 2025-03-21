from config.settings import Settings
from app.nvidia_api.image_client import NvidiaImageClient
from app.gemini_api.gemini_image_client import GeminiImageClient
from typing import Dict, List, Any
import asyncio
import time
import random
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageService:
    """Service for educational image generation"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.image_client = NvidiaImageClient(settings)
        self.gemini_client = GeminiImageClient(settings)
        
    async def generate_image(self, prompt: str) -> str:
        """
        Generate an image based on a text prompt using NVIDIA API.
        
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
    
    async def generate_gemini_image(self, prompt: str, filename_prefix: str = None) -> Dict[str, Any]:
        """
        Generate an image based on a text prompt using Google's Gemini API.
        
        This function is optimized for parallel calls from the frontend.
        
        Args:
            prompt: Text prompt for image generation
            filename_prefix: Optional prefix for the generated filename
            
        Returns:
            Dictionary containing success status, image URL, and any error message
        """
        logger.info(f"Starting Gemini image generation for prompt: {prompt[:50]}...")
        logger.info(f"USE_MOCK_DATA is set to: {self.settings.USE_MOCK_DATA}")
        
        # Force mock mode to off for image generation
        original_mock_setting = self.settings.USE_MOCK_DATA
        self.settings.USE_MOCK_DATA = False
        logger.info(f"Forced USE_MOCK_DATA to: {self.settings.USE_MOCK_DATA}")
        
        try:
            if self.settings.USE_MOCK_DATA:
                # For development/demo, return a placeholder image URL
                logger.info("Using mock data for image generation")
                mock_url = self._generate_mock_image(prompt)
                return {
                    "success": True,
                    "image_url": mock_url,
                    "file_path": None,
                    "error": None
                }
            
            # Enhance the prompt for educational context
            enhanced_prompt = self._enhance_prompt(prompt)
            logger.info(f"Enhanced prompt: {enhanced_prompt[:50]}...")
            
            # Call Gemini's text-to-image API
            logger.info("Calling Gemini image client...")
            result = await self.gemini_client.generate_image(enhanced_prompt, filename_prefix)
            logger.info(f"Gemini image generation result: {result}")
            
            return result
        except Exception as e:
            logger.error(f"Error in generate_gemini_image: {str(e)}")
            return {
                "success": False,
                "image_url": None,
                "file_path": None,
                "error": str(e)
            }
        finally:
            # Restore original mock setting
            self.settings.USE_MOCK_DATA = original_mock_setting
            logger.info(f"Restored USE_MOCK_DATA to: {self.settings.USE_MOCK_DATA}")
    
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
