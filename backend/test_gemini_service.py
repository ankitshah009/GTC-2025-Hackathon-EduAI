#!/usr/bin/env python3
"""
Test script for the Gemini image generation service in the backend.
This script tests the ImageService's generate_gemini_image method.
"""

import asyncio
import os
import sys
from config.settings import get_settings
from app.services.image_service import ImageService

async def test_gemini_image_service():
    print("Testing Gemini image generation service...")
    
    # Get settings
    settings = get_settings()
    
    # If API key is provided as argument, use it
    if len(sys.argv) > 1:
        os.environ["GEMINI_API_KEY"] = sys.argv[1]
        print(f"Using API key from command line argument")
    
    # Initialize the image service
    image_service = ImageService(settings)
    
    # Test prompt
    prompt = "Create a visual representation of the water cycle showing evaporation, condensation, and precipitation"
    
    print(f"Generating image with prompt: {prompt}")
    result = await image_service.generate_gemini_image(prompt, filename_prefix="water_cycle")
    
    if result["success"]:
        print(f"✅ Image generated successfully!")
        print(f"Image saved at: {result['file_path']}")
        print(f"Image URL: {result['image_url']}")
    else:
        print(f"❌ Image generation failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_gemini_image_service())
