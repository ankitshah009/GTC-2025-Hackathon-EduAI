"""
Standalone script for testing Google Gemini image generation.

NOTE: This is a standalone script for testing. The actual functionality
has been integrated into the backend at:
- app/gemini_api/gemini_image_client.py (API client)
- app/services/image_service.py (service layer)

To use this in the backend, call ImageService.generate_gemini_image()
"""

import base64
import os
import uuid
import logging
import re
import json
from pathlib import Path
from typing import Optional, Tuple
import google.generativeai as genai
from google.generativeai import types
from PIL import Image
from io import BytesIO


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def save_binary_file(file_path: str, data: bytes) -> None:
    """Save binary data to a file.
    
    Args:
        file_path: Path where the file should be saved
        data: Binary data to save
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(data)
        logger.info(f"Successfully saved file to {file_path}")
    except Exception as e:
        logger.error(f"Error saving file to {file_path}: {str(e)}")
        raise


def extract_base64_image(text: str) -> Optional[bytes]:
    """Extract base64 encoded image from text."""
    try:
        # Pattern to find base64 encoded images
        pattern = r'data:image/(jpeg|png|gif);base64,([^"\']*)'
        matches = re.search(pattern, text)
        
        if matches:
            # Extract the base64 data
            img_type = matches.group(1)
            base64_data = matches.group(2)
            logger.info(f"Found base64 image with type: {img_type}")
            
            # Decode the base64 data
            image_data = base64.b64decode(base64_data)
            return image_data
            
        # Try to find a raw base64 string (without prefix)
        base64_chunks = re.findall(r'[A-Za-z0-9+/=]{100,}', text)
        if base64_chunks:
            longest_chunk = max(base64_chunks, key=len)
            logger.info(f"Found potential raw base64 data of length {len(longest_chunk)}")
            
            # Add padding if needed
            padding = 4 - (len(longest_chunk) % 4) if len(longest_chunk) % 4 else 0
            padded_data = longest_chunk + ('=' * padding)
            
            # Try to decode it
            try:
                image_data = base64.b64decode(padded_data)
                logger.info(f"Successfully decoded raw base64 data of length {len(image_data)}")
                return image_data
            except Exception as e:
                logger.error(f"Failed to decode raw base64 data: {e}")
                
    except Exception as e:
        logger.error(f"Error extracting base64 image: {e}")
        
    return None


def save_response_for_debugging(response, file_path: str) -> None:
    """Save the API response for debugging purposes."""
    try:
        # Create a serializable dictionary from the response
        debug_info = {
            "has_candidates": hasattr(response, "candidates"),
            "num_candidates": len(response.candidates) if hasattr(response, "candidates") else 0
        }
        
        if hasattr(response, "candidates") and len(response.candidates) > 0:
            candidate = response.candidates[0]
            debug_info["candidate_info"] = {
                "has_content": hasattr(candidate, "content"),
                "has_parts": hasattr(candidate.content, "parts") if hasattr(candidate, "content") else False,
                "num_parts": len(candidate.content.parts) if hasattr(candidate, "content") and hasattr(candidate.content, "parts") else 0
            }
            
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts") and len(candidate.content.parts) > 0:
                parts = candidate.content.parts
                debug_info["parts_info"] = []
                
                for i, part in enumerate(parts):
                    part_info = {
                        "part_index": i,
                        "part_type": str(type(part)),
                        "has_text": hasattr(part, "text") and part.text is not None,
                        "has_inline_data": hasattr(part, "inline_data") and part.inline_data is not None,
                    }
                    
                    if hasattr(part, "text") and part.text is not None:
                        part_info["text_preview"] = part.text[:100] + "..." if len(part.text) > 100 else part.text
                        part_info["text_length"] = len(part.text)
                        
                    if hasattr(part, "inline_data") and part.inline_data is not None:
                        part_info["mime_type"] = getattr(part.inline_data, "mime_type", "unknown")
                        part_info["data_length"] = len(part.inline_data.data) if hasattr(part.inline_data, "data") else 0
                        
                    debug_info["parts_info"].append(part_info)
        
        # Save to file
        with open(file_path, "w") as f:
            json.dump(debug_info, f, indent=2)
            
        logger.info(f"Debug info saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving debug info: {e}")


def generate_image(prompt: str, output_dir: str = "generated_images", filename_prefix: str = None) -> Tuple[bool, str]:
    """Generate an image using Google's Gemini API based on the provided prompt.
    
    This function is designed to be called multiple times in parallel from the frontend.
    It handles API key validation, prompt processing, image generation, and saving the result.
    
    Args:
        prompt: The text prompt describing the image to generate
        output_dir: Directory where images will be saved
        filename_prefix: Optional prefix for the generated filename
        
    Returns:
        Tuple containing (success_status, file_path_or_error_message)
    """
    try:
        # Get API key from environment variables
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            error_msg = "GEMINI_API_KEY environment variable not set"
            logger.error(error_msg)
            return False, error_msg
        
        # Initialize Gemini API
        logger.info("Initializing Gemini API...")
        genai.configure(api_key=api_key)
        
        # Define the model to use
        model = "gemini-2.0-flash-exp-image-generation"
        model_client = genai.GenerativeModel(model_name=model)
        
        # Generate a unique filename for output files
        unique_id = str(uuid.uuid4())[:8]
        prefix = filename_prefix if filename_prefix else "image"
        sanitized_prefix = ''.join(c if c.isalnum() or c == '_' else '_' for c in prefix[:10])
        filename = f"{sanitized_prefix}_{unique_id}.png"
        debug_filename = f"{sanitized_prefix}_{unique_id}_debug.json"
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        debug_path = os.path.join(output_dir, debug_filename)
        
        # Generate the image
        logger.info(f"Generating image with prompt: {prompt[:50]}...")
        response = model_client.generate_content(
            contents=prompt,
            generation_config={
                "response_mime_type": "image/png"
            }
        )
        
        # Save response for debugging
        save_response_for_debugging(response, debug_path)
        
        # Check for valid response
        if not hasattr(response, 'candidates') or len(response.candidates) == 0:
            error_msg = "No candidates found in response"
            logger.error(error_msg)
            return False, error_msg
            
        # Extract image data (from various possible response formats)
        image_data = None
        response_text = None
        
        # Process each part of the response
        for part in response.candidates[0].content.parts:
            # Check for text that might contain a base64 encoded image
            if hasattr(part, 'text') and part.text is not None:
                response_text = part.text
                logger.info(f"Found text response of length {len(response_text)}")
                
                # Try to extract base64 image from text
                extracted_image = extract_base64_image(response_text)
                if extracted_image:
                    logger.info("Successfully extracted image from text")
                    image_data = extracted_image
                    break
            
            # Check for inline image data
            if hasattr(part, 'inline_data') and part.inline_data is not None:
                mime_type = getattr(part.inline_data, 'mime_type', 'image/png')
                logger.info(f"Found inline data with mime type: {mime_type}")
                
                if hasattr(part.inline_data, 'data'):
                    image_data = part.inline_data.data
                    logger.info(f"Extracted binary data of length {len(image_data)}")
                    break
                    
        # If no image data was found but we have text, save text for inspection
        if image_data is None and response_text:
            text_path = os.path.join(output_dir, f"{sanitized_prefix}_{unique_id}_text.txt")
            with open(text_path, "w") as f:
                f.write(response_text)
            logger.info(f"No image data found, saved text response to {text_path}")
            
            # As a last resort, try to extract base64 again with the entire text
            extracted_image = extract_base64_image(response_text)
            if extracted_image:
                logger.info("Successfully extracted image from full text")
                image_data = extracted_image
        
        # If no image data found, return error
        if image_data is None:
            error_msg = "No image data found in the response"
            logger.error(error_msg)
            return False, error_msg
            
        # Save the raw binary data first for inspection
        raw_path = os.path.join(output_dir, f"{sanitized_prefix}_{unique_id}_raw.bin")
        with open(raw_path, "wb") as f:
            f.write(image_data)
        logger.info(f"Saved raw binary data to {raw_path}")
        
        # Try to convert to a proper PNG image using PIL
        try:
            logger.info("Attempting to open image with PIL...")
            img = Image.open(BytesIO(image_data))
            logger.info(f"Successfully opened image: format={img.format}, size={img.size}, mode={img.mode}")
            
            # Convert to RGB or RGBA and save as PNG
            img = img.convert("RGBA" if img.mode == "RGBA" else "RGB")
            img.save(file_path, "PNG")
            logger.info(f"Successfully saved processed image to {file_path}")
            return True, file_path
            
        except Exception as pil_error:
            logger.error(f"Error processing image with PIL: {pil_error}")
            
            # Create a fallback image with error message
            try:
                logger.info("Creating fallback image...")
                img = Image.new('RGB', (800, 600), color=(255, 255, 255))
                
                # Import here to avoid issues if it fails
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                
                # Add error message and prompt
                draw.text((50, 50), f"Failed to process image: {str(pil_error)}", fill=(255, 0, 0))
                draw.text((50, 100), f"Prompt: {prompt[:200]}", fill=(0, 0, 0))
                
                # Save the image
                img.save(file_path, "PNG")
                logger.info(f"Saved fallback image to {file_path}")
                return True, file_path
                
            except Exception as fallback_error:
                logger.error(f"Error creating fallback image: {fallback_error}")
                return False, f"Failed to process image: {pil_error}"
            
    except Exception as e:
        error_msg = f"Error generating image: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


# This function can be imported directly by the backend
def generate_image_for_backend(prompt: str, output_dir: str = "static/generated_images", 
                               filename_prefix: str = None) -> dict:
    """Backend-friendly wrapper for generate_image.
    
    This function is designed to be imported and used by the backend.
    
    Args:
        prompt: The text prompt describing the image to generate
        output_dir: Directory where images will be saved
        filename_prefix: Optional prefix for the generated filename
        
    Returns:
        A dictionary containing:
        - success: bool indicating if the operation was successful
        - file_path: path to the generated image (if successful)
        - error: error message (if not successful)
    """
    success, result = generate_image(prompt, output_dir, filename_prefix)
    if success:
        return {
            "success": True,
            "file_path": result,
            "error": None
        }
    else:
        return {
            "success": False,
            "file_path": None,
            "error": result
        }


if __name__ == "__main__":
    # Example usage when script is run directly (for testing only)
    example_prompt = """Generate an image of a futuristic, sustainable city on Mars, 
    incorporating elements of both Martian geography and eco-friendly architecture from Earth, 
    with a style reminiscent of Syd Mead's concept art."""
    
    success, result = generate_image(example_prompt, filename_prefix="mars_city")
    if success:
        print(f"Image generated successfully: {result}")
    else:
        print(f"Image generation failed: {result}")
