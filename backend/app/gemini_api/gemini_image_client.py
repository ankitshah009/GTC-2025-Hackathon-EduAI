from config.settings import Settings
from google import genai
from google.genai import types
import logging
import os
import uuid
import time
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
        
        logger.info(f"GeminiImageClient initialized with API key: {self.api_key[:4]}...{self.api_key[-4:]}")
        logger.info(f"Using model: {self.model}")
        logger.info(f"Output directory: {self.output_dir}")
    
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
            
            # Check if API key is present
            if not self.api_key:
                error_msg = "GEMINI_API_KEY is not set or is empty"
                logger.error(error_msg)
                return {
                    "success": False,
                    "file_path": None,
                    "image_url": None,
                    "error": error_msg
                }
            
            # Initialize client
            logger.info("Initializing Gemini client...")
            client = genai.Client(api_key=self.api_key)
            
            # Generate image using Gemini
            logger.info(f"Calling Gemini model {self.model}...")
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
            
            logger.info(f"Response received, type: {type(response)}")
            
            # Generate a unique filename
            unique_id = str(uuid.uuid4())[:8]
            prefix = filename_prefix if filename_prefix else "image"
            sanitized_prefix = ''.join(c if c.isalnum() or c == '_' else '_' for c in prefix)
            filename = f"{sanitized_prefix}_{unique_id}.png"
            file_path = os.path.join(self.output_dir, filename)
            
            logger.info(f"Will save to file path: {file_path}")
            
            # Process response to extract and save image
            if not hasattr(response, 'candidates') or len(response.candidates) == 0:
                error_msg = "No candidates found in the response"
                logger.error(error_msg)
                return {
                    "success": False,
                    "file_path": None,
                    "image_url": None,
                    "error": error_msg
                }
                
            if not hasattr(response.candidates[0], 'content') or not hasattr(response.candidates[0].content, 'parts'):
                error_msg = "No content or parts found in the response"
                logger.error(error_msg)
                return {
                    "success": False,
                    "file_path": None,
                    "image_url": None,
                    "error": error_msg
                }
            
            image_found = False
            for part in response.candidates[0].content.parts:
                logger.info(f"Processing part: {type(part)}")
                
                if hasattr(part, 'text') and part.text is not None:
                    logger.info(f"Text response: {part.text}")
                
                if hasattr(part, 'inline_data') and part.inline_data is not None:
                    logger.info(f"Found inline data with mime type: {getattr(part.inline_data, 'mime_type', 'unknown')}")
                    # Save the image
                    logger.info(f"Image generated successfully, saving to {file_path}...")
                    try:
                        with open(file_path, "wb") as f:
                            f.write(part.inline_data.data)
                        
                        # Get the relative path for URL generation
                        rel_path = os.path.relpath(file_path, self.settings.STATIC_DIR)
                        image_url = f"/static/{rel_path}"
                        
                        logger.info(f"Image saved successfully, URL: {image_url}")
                        image_found = True
                        
                        # Add a small delay to ensure file is written
                        time.sleep(0.5)
                        
                        return {
                            "success": True,
                            "file_path": file_path,
                            "image_url": image_url,
                            "error": None
                        }
                    except Exception as e:
                        error_msg = f"Error saving image file: {str(e)}"
                        logger.error(error_msg)
                        return {
                            "success": False,
                            "file_path": None,
                            "image_url": None,
                            "error": error_msg
                        }
            
            # If we get here, no image was found
            error_msg = "No image data found in the response"
            logger.error(error_msg)
            logger.error(f"Full response: {str(response)}")
            return {
                "success": False,
                "file_path": None,
                "image_url": None,
                "error": error_msg
            }
                
        except Exception as e:
            error_msg = f"Error generating image with Gemini API: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "file_path": None,
                "image_url": None,
                "error": error_msg
            }
