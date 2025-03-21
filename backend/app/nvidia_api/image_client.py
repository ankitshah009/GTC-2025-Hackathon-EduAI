from config.settings import Settings
import aiohttp
import json
from typing import Dict, Any

class NvidiaImageClient:
    """Client for NVIDIA's text-to-image API endpoints"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = settings.NVIDIA_API_BASE_URL
        self.api_key = settings.NVIDIA_API_KEY
        self.model_id = settings.IMAGE_MODEL_ID
    
    async def generate_image(self, prompt: str) -> str:
        """
        Generate an image using NVIDIA's text-to-image API.
        
        Args:
            prompt: Text prompt for image generation
            
        Returns:
            URL to the generated image
        """
        # If using mock data, don't call the API
        if self.settings.USE_MOCK_DATA:
            raise Exception("API should not be called in mock mode")
        
        # Prepare API request payload
        payload = {
            "model": self.model_id,
            "prompt": prompt,
            "n": 1,
            "size": self.settings.IMAGE_SIZE
        }
        
        # Prepare API request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Call NVIDIA's text-to-image API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/image",
                headers=headers,
                json=payload
            ) as response:
                # Check for successful response
                if response.status != 200:
                    error_data = await response.text()
                    raise Exception(f"NVIDIA image API error ({response.status}): {error_data}")
                
                # Parse response
                data = await response.json()
                
                # Extract image URL from the response
                # Note: Adjust based on actual API response structure
                image_url = data.get("image_url", "")
                
                return image_url
