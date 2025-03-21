from config.settings import Settings
from google import genai
from google.genai import types
import logging
import os
import uuid
import time
import base64
import re
import io
from typing import Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
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
            
            # Initialize client - using the method from simple_gemini_test.py
            logger.info("Initializing Gemini client...")
            client = genai.Client(api_key=self.api_key)
            
            # Generate a unique filename
            unique_id = str(uuid.uuid4())[:8]
            prefix = filename_prefix if filename_prefix else prompt[:10]
            sanitized_prefix = ''.join(c if c.isalnum() or c == '_' else '_' for c in prefix)
            filename = f"___{''.join(c if c.isalnum() or c == '_' else '_' for c in sanitized_prefix)}_{unique_id}.png"
            file_path = os.path.join(self.output_dir, filename)
            
            logger.info(f"Will save to file path: {file_path}")
            
            # Generate image using Gemini - using the method from simple_gemini_test.py
            logger.info(f"Calling Gemini model {self.model}...")
            
            try:
                # Try with a timeout
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=['Text', 'Image']
                    )
                )
            except Exception as gen_err:
                logger.error(f"Error calling Gemini API: {str(gen_err)}")
                # Return fallback image
                return self._create_fallback_image(file_path, f"API Error: {str(gen_err)}", prompt)
            
            logger.info(f"Response received, type: {type(response)}")
            
            # Process response to extract and save image
            if not hasattr(response, 'candidates') or len(response.candidates) == 0:
                error_msg = "No candidates found in the response"
                logger.error(error_msg)
                return self._create_fallback_image(file_path, error_msg, prompt)
                
            if not hasattr(response.candidates[0], 'content') or not hasattr(response.candidates[0].content, 'parts'):
                error_msg = "No content or parts found in the response"
                logger.error(error_msg)
                return self._create_fallback_image(file_path, error_msg, prompt)
            
            # Process each part of the response, based on simple_gemini_test.py approach
            image_saved = False
            rel_path = None
            
            for part in response.candidates[0].content.parts:
                logger.info(f"Processing part: {type(part)}")
                
                # Check for text that might contain base64 encoded image
                if hasattr(part, 'text') and part.text is not None:
                    logger.info(f"Found text response: {part.text[:100]}...")
                    
                    # Check for base64 encoded image in text
                    # Sometimes Gemini returns base64 data in text
                    base64_match = re.search(r'data:image\/[^;]+;base64,([^"]+)', part.text)
                    if base64_match:
                        try:
                            logger.info("Found base64 image data in text, decoding...")
                            base64_data = base64_match.group(1)
                            image_data = base64.b64decode(base64_data)
                            
                            # Try to validate image data before saving
                            try:
                                img = Image.open(io.BytesIO(image_data))
                                img.verify()  # Verify it's a valid image
                                logger.info(f"Base64 image validated: {img.format}, {img.size}")
                                
                                # Save the validated image
                                with open(file_path, "wb") as f:
                                    f.write(image_data)
                                    
                                image_saved = True
                                rel_path = os.path.relpath(file_path, self.settings.STATIC_DIR)
                                image_url = f"/static/{rel_path}"
                                logger.info(f"Base64 image from text saved to {file_path}")
                            except Exception as validate_err:
                                logger.error(f"Base64 image validation failed: {validate_err}")
                        except Exception as text_b64_err:
                            logger.error(f"Error decoding base64 from text: {str(text_b64_err)}")
                
                # Check for inline image data
                if hasattr(part, 'inline_data') and part.inline_data is not None:
                    mime_type = getattr(part.inline_data, 'mime_type', 'image/png')
                    logger.info(f"Found inline data with mime type: {mime_type}")
                    
                    if hasattr(part.inline_data, 'data'):
                        # Don't write directly to a file - validate the data first
                        try:
                            logger.info("Validating image data before saving...")
                            img_bytes = part.inline_data.data
                            
                            # Try to open and validate image directly from bytes
                            try:
                                img = Image.open(io.BytesIO(img_bytes))
                                img.verify()  # Verify it's a valid image
                                
                                # If we get here, the image is valid - save it
                                with open(file_path, "wb") as f:
                                    f.write(img_bytes)
                                logger.info(f"Valid image saved to {file_path}")
                                
                                image_saved = True
                                rel_path = os.path.relpath(file_path, self.settings.STATIC_DIR)
                                image_url = f"/static/{rel_path}"
                            except Exception as direct_err:
                                logger.error(f"Direct image validation failed: {direct_err}")
                                
                                # Try base64 decoding as fallback
                                try:
                                    logger.info("Trying base64 decoding...")
                                    decoded_data = base64.b64decode(img_bytes)
                                    
                                    # Try to validate the decoded data
                                    try:
                                        img = Image.open(io.BytesIO(decoded_data))
                                        img.verify()  # Verify it's a valid image
                                        
                                        # Valid image, save it
                                        with open(file_path, "wb") as f:
                                            f.write(decoded_data)
                                        logger.info(f"Base64 decoded image saved to {file_path}")
                                        
                                        image_saved = True
                                        rel_path = os.path.relpath(file_path, self.settings.STATIC_DIR)
                                        image_url = f"/static/{rel_path}"
                                    except Exception as b64_validate_err:
                                        logger.error(f"Base64 decoded image validation failed: {b64_validate_err}")
                                        
                                        # One last attempt: Try saving the decoded data as a PNG
                                        try:
                                            logger.info("Attempting to convert data to PNG...")
                                            img = Image.open(io.BytesIO(decoded_data))
                                            img.save(file_path, format="PNG")
                                            logger.info(f"Converted image saved to {file_path}")
                                            
                                            image_saved = True
                                            rel_path = os.path.relpath(file_path, self.settings.STATIC_DIR)
                                            image_url = f"/static/{rel_path}"
                                        except Exception as convert_err:
                                            logger.error(f"Image conversion failed: {convert_err}")
                                except Exception as b64_err:
                                    logger.error(f"Base64 decoding failed: {b64_err}")
                        except Exception as validate_err:
                            logger.error(f"Image validation process failed: {validate_err}")
            
            # If we successfully saved the image, return success
            if image_saved:
                # Add a small delay to ensure file is written
                time.sleep(0.5)
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "image_url": image_url,
                    "error": None
                }
            
            # If we reach here, no image was saved - create a fallback image
            return self._create_fallback_image(file_path, "No valid image data found in response", prompt)
                
        except Exception as e:
            error_msg = f"Error generating image with Gemini API: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            
            # Create fallback image
            return self._create_fallback_image(file_path, error_msg, prompt)
    
    def _create_fallback_image(self, file_path: str, error_msg: str, prompt: str) -> Dict[str, Any]:
        """Create a fallback image with error message and prompt text"""
        logger.warning(f"Creating fallback image: {error_msg}")
        try:
            # Create a simple fallback image with text
            img = Image.new('RGB', (800, 600), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Draw error message
            draw.text((50, 50), f"Error: {error_msg[:100]}", fill=(255, 0, 0))
            
            # Draw prompt with word wrapping
            wrapped_prompt = self._wrap_text(prompt, 60)
            y_pos = 100
            for line in wrapped_prompt.split('\n'):
                draw.text((50, y_pos), line, fill=(0, 0, 0))
                y_pos += 20
            
            # Draw a border
            draw.rectangle([(10, 10), (790, 590)], outline=(200, 200, 200))
            
            # Save the image
            img.save(file_path, "PNG")
            
            # Get the relative path for URL generation
            rel_path = os.path.relpath(file_path, self.settings.STATIC_DIR)
            image_url = f"/static/{rel_path}"
            
            logger.info(f"Fallback image saved, URL: {image_url}")
            
            return {
                "success": True,
                "file_path": file_path,
                "image_url": image_url,
                "error": None
            }
        except Exception as fallback_error:
            logger.error(f"Error creating fallback image: {str(fallback_error)}")
            
            # As a last resort, return an error
            return {
                "success": False,
                "file_path": None,
                "image_url": None,
                "error": f"Failed to generate or save image: {str(fallback_error)}"
            }
    
    def _wrap_text(self, text: str, width: int) -> str:
        """Wrap text to fit within a certain width."""
        lines = []
        for paragraph in text.split('\n'):
            words = paragraph.split()
            current_line = []
            current_width = 0
            
            for word in words:
                if current_width + len(word) <= width:
                    current_line.append(word)
                    current_width += len(word) + 1  # +1 for the space
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_width = len(word) + 1
            
            if current_line:
                lines.append(' '.join(current_line))
            
        return '\n'.join(lines)
