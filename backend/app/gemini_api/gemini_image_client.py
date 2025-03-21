from config.settings import Settings
from google import genai
from google.genai import types
import logging
import os
import uuid
from typing import Dict, Any, Tuple
from PIL import Image
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GeminiImageClient:
    """Client for Google's Gemini API for image generation"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = os.environ.get("GEMINI_API_KEY", settings.GEMINI_API_KEY)
        self.model = "gemini-2.0-flash-exp-image-generation"
        self.output_dir = os.path.join(settings.STATIC_DIR, "generated_images")
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_image(self, prompt: str, filename_prefix: str = None) -> Dict[str, Any]:
        """
        Generate an image using Google's Gemini API.
        
        Args:
            prompt: Text prompt for image generation
            filename_prefix: Optional prefix for the generated filename
            
        Returns:
            Dictionary containing success status, file path, and any error message
        """
        try:
            logger.info(f"Generating image with prompt: {prompt[:50]}...")
            
            # Initialize client
            client = genai.Client(api_key=self.api_key)
            
            # Generate image using Gemini
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
            
            # Generate a unique filename
            unique_id = str(uuid.uuid4())[:8]
            prefix = filename_prefix if filename_prefix else "image"
            filename = f"{prefix}_{unique_id}.png"
            file_path = os.path.join(self.output_dir, filename)
            
            # Process response to extract and save image
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    logger.info(f"Text response: {part.text}")
                elif part.inline_data is not None:
                    # Save the image
                    logger.info(f"Image generated successfully, saving to {file_path}...")
                    with open(file_path, "wb") as f:
                        f.write(part.inline_data.data)
                    
                    # Get the relative path for URL generation
                    rel_path = os.path.relpath(file_path, self.settings.STATIC_DIR)
                    image_url = f"/static/{rel_path}"
                    
                    return {
                        "success": True,
                        "file_path": file_path,
                        "image_url": image_url,
                        "error": None
                    }
            
            # If we get here, no image was found
            error_msg = "No image data found in the response"
            logger.error(error_msg)
            return {
                "success": False,
                "file_path": None,
                "image_url": None,
                "error": error_msg
            }
                
        except Exception as e:
            error_msg = f"Error generating image with Gemini API: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "file_path": None,
                "image_url": None,
                "error": error_msg
            }
