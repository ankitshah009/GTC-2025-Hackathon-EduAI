import os
import sys
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now import the modules
from backend.config.settings import get_settings
from backend.app.services.image_service import ImageService

async def test_gemini_image_generation():
    print("Testing Gemini image generation...")
    
    # Get settings and initialize the image service
    settings = get_settings()
    image_service = ImageService(settings)
    
    # Set test API key for this run if provided as argument
    if len(sys.argv) > 1:
        os.environ["GEMINI_API_KEY"] = sys.argv[1]
        print(f"Using provided API key: {sys.argv[1][:5]}...")
    
    # Test prompt
    prompt = "Generate an image of a futuristic classroom with holographic displays and robot teaching assistants"
    
    print(f"Generating image with prompt: {prompt}")
    result = await image_service.generate_gemini_image(prompt, filename_prefix="test_classroom")
    
    if result["success"]:
        print(f"✅ Image generated successfully!")
        print(f"Image saved at: {result['file_path']}")
        print(f"Image URL: {result['image_url']}")
    else:
        print(f"❌ Image generation failed: {result['error']}")
    
    return result

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_gemini_image_generation())
    
    # Exit with appropriate status code
    sys.exit(0 if result["success"] else 1)
