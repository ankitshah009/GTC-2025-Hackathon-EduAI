from config.settings import Settings
import google.generativeai as genai
from google.generativeai import types
import logging
import os
import uuid
from typing import Dict, Any, Tuple

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
        
        # Initialize the client
        genai.configure(api_key=self.api_key)
        self.client = genai.Client(api_key=self.api_key)
    
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
            
            # Create the content request
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                ),
            ]
            
            # Make the API call
            response = self.client.generate_content(
                model=self.model,
                contents=contents,
                generation_config={"response_mime_type": "image/png"},
            )
            
            # Process the response
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                parts = response.candidates[0].content.parts
                if len(parts) > 0 and hasattr(parts[0], 'data'):
                    # Get the image data
                    image_data = parts[0].data
                    
                    # Generate a unique filename
                    unique_id = str(uuid.uuid4())[:8]
                    prefix = filename_prefix if filename_prefix else "image"
                    filename = f"{prefix}_{unique_id}.png"
                    file_path = os.path.join(self.output_dir, filename)
                    
                    # Save the image
                    with open(file_path, "wb") as f:
                        f.write(image_data)
                    
                    logger.info(f"Image successfully generated and saved to {file_path}")
                    
                    # Get the relative path for URL generation
                    rel_path = os.path.relpath(file_path, self.settings.STATIC_DIR)
                    image_url = f"/static/{rel_path}"
                    
                    return {
                        "success": True,
                        "file_path": file_path,
                        "image_url": image_url,
                        "error": None
                    }
                else:
                    error_msg = "No image data in response"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "file_path": None,
                        "image_url": None,
                        "error": error_msg
                    }
            else:
                error_msg = "No valid response received from Gemini API"
                logger.error(error_msg)
                return {
                    "success": False,
                    "file_path": None,
                    "image_url": None,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error generating image: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "file_path": None,
                "image_url": None,
                "error": error_msg
            }
