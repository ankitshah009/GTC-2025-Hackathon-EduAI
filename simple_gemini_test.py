#!/usr/bin/env python3
"""
Simple standalone test for Google Gemini image generation.
This doesn't depend on the backend structure.
"""

import os
import sys
import logging
from pathlib import Path
import uuid
import base64
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_gemini_image_generation(api_key, prompt):
    """Test Gemini image generation with provided API key and prompt."""
    try:
        logger.info("Initializing Gemini client...")
        client = genai.Client(api_key=api_key)
        
        # Define output directory
        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)
        
        # Create unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"test_image_{unique_id}.png"
        file_path = os.path.join(output_dir, filename)
        
        logger.info(f"Generating image with prompt: {prompt[:50]}...")
        
        # Generate image using Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )
        
        # Process response
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Response structure: {dir(response)}")
        
        image_saved = False
        for part in response.candidates[0].content.parts:
            logger.info(f"Part type: {type(part)}")
            logger.info(f"Part attributes: {dir(part)}")
            
            if hasattr(part, 'text') and part.text:
                logger.info(f"Text response: {part.text}")
            
            if hasattr(part, 'inline_data') and part.inline_data:
                logger.info(f"Inline data type: {type(part.inline_data)}")
                logger.info(f"Inline data attributes: {dir(part.inline_data)}")
                
                if hasattr(part.inline_data, 'mime_type'):
                    logger.info(f"MIME type: {part.inline_data.mime_type}")
                
                if hasattr(part.inline_data, 'data'):
                    # Try to save the raw data first
                    try:
                        logger.info("Saving raw binary data...")
                        with open(file_path, "wb") as f:
                            f.write(part.inline_data.data)
                        image_saved = True
                        logger.info(f"Image saved to {file_path}")
                    except Exception as e:
                        logger.error(f"Error saving raw data: {str(e)}")
                        
                        # Try base64 decoding as fallback
                        try:
                            logger.info("Trying base64 decoding...")
                            decoded_data = base64.b64decode(part.inline_data.data)
                            with open(file_path, "wb") as f:
                                f.write(decoded_data)
                            image_saved = True
                            logger.info(f"Base64 decoded image saved to {file_path}")
                        except Exception as e2:
                            logger.error(f"Error saving base64 decoded data: {str(e2)}")
        
        if image_saved:
            return True, file_path
        else:
            error_msg = "No image data could be saved from the response"
            logger.error(error_msg)
            return False, error_msg
            
    except Exception as e:
        error_msg = f"Error generating image: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

if __name__ == "__main__":
    # Get API key from command line or environment
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not provided. Please provide it as an argument or set it as an environment variable.")
            sys.exit(1)
    
    # Set test prompt
    prompt = "Generate an image of a futuristic classroom with holographic displays and robot teaching assistants"
    
    # Run the test
    success, result = test_gemini_image_generation(api_key, prompt)
    
    # Print result
    if success:
        print(f"✅ Image generated successfully!")
        print(f"Image saved at: {result}")
    else:
        print(f"❌ Image generation failed: {result}")
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
