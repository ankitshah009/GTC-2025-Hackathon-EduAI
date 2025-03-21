from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import ImageGenerationRequest, ImageResponse, GeminiImageResponse, ErrorResponse
from app.services.image_service import ImageService
from config.settings import get_settings
from typing import Dict, Any

router = APIRouter()

@router.post("/generate", response_model=ImageResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def generate_image(request: ImageGenerationRequest, settings=Depends(get_settings)):
    """
    Generate an educational image based on a text prompt using NVIDIA API.
    
    - **prompt**: Text prompt for image generation (e.g., "Educational diagram showing the process of photosynthesis")
    
    Returns:
    - **image_url**: URL to the generated image
    """
    try:
        # Initialize image service
        image_service = ImageService(settings)
        
        # Generate image
        image_url = await image_service.generate_image(prompt=request.prompt)
        
        return {"image_url": image_url}
    except Exception as e:
        # Log the error (in a real app, you'd use proper logging)
        print(f"Error generating image: {str(e)}")
        
        # Return a user-friendly error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate image. Please try again."
        )

@router.post("/generate-gemini", response_model=GeminiImageResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def generate_gemini_image(request: ImageGenerationRequest, settings=Depends(get_settings)):
    """
    Generate an educational image based on a text prompt using Google Gemini API.
    
    - **prompt**: Text prompt for image generation (e.g., "Educational diagram showing the process of photosynthesis")
    
    Returns:
    - **success**: Boolean indicating if the generation was successful
    - **image_url**: URL to the generated image
    - **error**: Error message if generation failed
    """
    try:
        # Initialize image service
        image_service = ImageService(settings)
        
        # Generate image using Gemini
        result = await image_service.generate_gemini_image(
            prompt=request.prompt, 
            filename_prefix=request.prompt[:10].replace(" ", "_")
        )
        
        if result["success"]:
            return {
                "success": True,
                "image_url": result["image_url"],
                "error": None
            }
        else:
            # Return the error from the Gemini API
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate image: {result['error']}"
            )
    except Exception as e:
        # Log the error
        print(f"Error generating image with Gemini: {str(e)}")
        
        # Return a user-friendly error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate image with Gemini. Please try again."
        )
