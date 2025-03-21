import base64
import os
import uuid
import logging
from pathlib import Path
from typing import Optional, Tuple
import google.generativeai as genai
from google.generativeai import types


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
        
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        
        # Define the model to use
        model = "gemini-2.0-flash-exp-image-generation"
        
        # Create the content request
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        
        # Generate the image
        logger.info(f"Generating image with prompt: {prompt[:50]}...")
        response = client.generate_content(
            model=model,
            contents=contents,
            generation_config={"response_mime_type": "image/png"},
        )
        
        # Generate a unique filename
        unique_id = str(uuid.uuid4())[:8]
        prefix = filename_prefix if filename_prefix else "image"
        filename = f"{prefix}_{unique_id}.png"
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        
        # Process the response
        if hasattr(response, 'candidates') and len(response.candidates) > 0:
            parts = response.candidates[0].content.parts
            if len(parts) > 0 and hasattr(parts[0], 'data'):
                image_data = parts[0].data
                # Save the image
                save_binary_file(file_path, image_data)
                logger.info(f"Image successfully generated and saved to {file_path}")
                return True, file_path
            else:
                error_msg = "No image data in response"
                logger.error(error_msg)
                return False, error_msg
        else:
            error_msg = "No valid response received from Gemini API"
            logger.error(error_msg)
            return False, error_msg
            
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
