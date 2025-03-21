#!/usr/bin/env python3
"""
Test script for the LLM client integration.
This script demonstrates how to use the OpenAI client with NVIDIA's Nemotron model.
"""

import asyncio
import os
from dotenv import load_dotenv
from app.nvidia_api.llm_client import LLMClient
from config.settings import Settings

async def test_llm_client():
    """Test the LLM client with a simple prompt"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Create settings with USE_MOCK_DATA set to False to force API calls
    settings = Settings()
    settings.USE_MOCK_DATA = False
    
    # Print configuration
    print(f"Using API type: {settings.LLM_API_TYPE}")
    print(f"Base URL: {settings.LLM_API_BASE_URL}")
    print(f"Model: {settings.LLM_MODEL_ID}")
    
    # Create LLM client
    llm_client = LLMClient(settings)
    
    # Test prompt
    prompt = "Explain the concept of machine learning to a high school student in 3-4 paragraphs."
    
    print("\nGenerating text using the standard API...")
    try:
        # Test regular API
        response = await llm_client.generate_text(prompt)
        print("\nResponse from LLM:")
        print("=" * 80)
        print(response)
        print("=" * 80)
    except Exception as e:
        print(f"Error using standard API: {str(e)}")
    
    print("\nGenerating text using the streaming API...")
    try:
        # Test streaming API
        print("\nStreaming response from LLM:")
        print("=" * 80)
        
        # Collect the full response for comparison
        full_response = ""
        
        async for chunk in llm_client.generate_text_stream(prompt):
            print(chunk, end="")
            full_response += chunk
        
        print("\n" + "=" * 80)
    except Exception as e:
        print(f"Error using streaming API: {str(e)}")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_llm_client())
