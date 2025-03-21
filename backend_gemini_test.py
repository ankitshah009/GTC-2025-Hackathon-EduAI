#!/usr/bin/env python3
"""
Backend-specific test for Gemini image generation.
This test checks the implementation in backend/app/gemini_api/gemini_image_client.py
"""

import os
import sys
import logging
from pathlib import Path
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Import the settings and client
from app.gemini_api.gemini_image_client import GeminiImageClient
from config.settings import Settings


async def test_backend_gemini_client():
    """Test the backend's GeminiImageClient implementation."""
    try:
        # Create settings with default values
        settings = Settings()
        
        # Set API key from environment or command line
        if len(sys.argv) > 1:
            os.environ["GEMINI_API_KEY"] = sys.argv[1]
        elif not os.environ.get("GEMINI_API_KEY"):
            # Try to read from .env file
            try:
                env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
                with open(env_path, "r") as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            key = line.strip().split("=", 1)[1]
                            os.environ["GEMINI_API_KEY"] = key
                            break
            except Exception as e:
                logger.error(f"Error reading API key from .env: {e}")
        
        # Check if API key is available
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not set. Please set it as an environment variable or provide it as an argument.")
            return False, "GEMINI_API_KEY not set"
            
        logger.info(f"Using API key: {api_key[:4]}...{api_key[-4:]}")
        
        # Create client
        client = GeminiImageClient(settings)
        
        # Set test prompt
        prompt = "Generate an image of a futuristic classroom with holographic displays and robot teaching assistants"
        
        # Call the generate_image method
        logger.info("Calling generate_image...")
        result = await client.generate_image(prompt, "test_backend")
        
        # Check the result
        if result["success"]:
            logger.info(f"✅ Image generated successfully!")
            logger.info(f"Image saved at: {result['file_path']}")
            logger.info(f"Image URL: {result['image_url']}")
            return True, result["file_path"]
        else:
            logger.error(f"❌ Image generation failed: {result['error']}")
            return False, result["error"]
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False, str(e)


if __name__ == "__main__":
    # Run the test
    result, message = asyncio.run(test_backend_gemini_client())
    
    # Print result
    if result:
        print(f"✅ Backend Gemini client test passed!")
        print(f"Image saved at: {message}")
    else:
        print(f"❌ Backend Gemini client test failed: {message}")
    
    # Exit with appropriate status code
    sys.exit(0 if result else 1)
