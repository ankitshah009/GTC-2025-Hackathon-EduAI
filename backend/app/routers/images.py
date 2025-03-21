from fastapi import APIRouter, Depends, HTTPException, Request
from app.models.schemas import ImageGenerationRequest, ImageResponse, GeminiImageResponse, ErrorResponse
from app.services.image_service import ImageService
from config.settings import get_settings
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate", response_model=ImageResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def generate_image(request: ImageGenerationRequest, req: Request, settings=Depends(get_settings)):
    """
    Generate an educational image based on a text prompt using NVIDIA API.
    
    - **prompt**: Text prompt for image generation (e.g., "Educational diagram showing the process of photosynthesis")
    
    Returns:
    - **image_url**: URL to the generated image
    """
    # Log the full request for debugging
    logger.info(f"Received image generation request: {request.prompt[:50]}...")
    if hasattr(request, 'timestamp'):
        logger.info(f"Request timestamp: {request.timestamp}")
    
    # Get client IP for logging
    client_host = req.client.host if req.client else "unknown"
    logger.info(f"Request from client: {client_host}")
    
    try:
        # Initialize image service
        image_service = ImageService(settings)
        
        # Generate image
        logger.info(f"Calling image service generate_image with prompt: {request.prompt[:50]}...")
        image_url = await image_service.generate_image(prompt=request.prompt)
        
        # Log the result
        logger.info(f"Image generation result - success: True")
        logger.info(f"Generated image URL: {image_url}")
        
        return {"image_url": image_url}
    except Exception as e:
        # Log the error
        logger.error(f"Error generating image: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Return a user-friendly error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate image. Please try again."
        )

@router.post("/generate-gemini", response_model=GeminiImageResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def generate_gemini_image(request: ImageGenerationRequest, req: Request, settings=Depends(get_settings)):
    """
    Generate an educational image based on a text prompt using Google Gemini API.
    
    - **prompt**: Text prompt for image generation (e.g., "Educational diagram showing the process of photosynthesis")
    
    Returns:
    - **success**: Boolean indicating if the generation was successful
    - **image_url**: URL to the generated image
    - **error**: Error message if generation failed
    """
    # Log the full request for debugging
    logger.info(f"Received image generation request: {request.prompt[:50]}...")
    if hasattr(request, 'timestamp'):
        logger.info(f"Request timestamp: {request.timestamp}")
    
    # Get client IP for logging
    client_host = req.client.host if req.client else "unknown"
    logger.info(f"Request from client: {client_host}")
    
    try:
        # Initialize image service
        image_service = ImageService(settings)
        
        # Sanitize the filename prefix to avoid any path issues
        filename_prefix = request.prompt[:10].replace(" ", "_")
        sanitized_prefix = ''.join(c if c.isalnum() or c == '_' else '_' for c in filename_prefix)
        logger.info(f"Using sanitized filename prefix: {sanitized_prefix}")
        
        # Generate image using Gemini
        logger.info(f"Calling image service generate_gemini_image with prompt: {request.prompt[:50]}...")
        result = await image_service.generate_gemini_image(
            prompt=request.prompt, 
            filename_prefix=sanitized_prefix
        )
        
        # Log the result
        logger.info(f"Image generation result - success: {result['success']}")
        if result['success']:
            logger.info(f"Generated image path: {result['file_path']}")
            logger.info(f"Image URL: {result['image_url']}")
        else:
            logger.error(f"Image generation failed: {result['error']}")
        
        if result["success"]:
            return {
                "success": True,
                "image_url": result["image_url"],
                "error": None
            }
        else:
            # Log additional error details
            logger.error(f"Details of failed image generation: {result}")
            
            # Return the error from the Gemini API
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate image: {result['error']}"
            )
    except Exception as e:
        # Log the error
        logger.error(f"Error generating image with Gemini: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Return a user-friendly error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate image with Gemini. Please try again."
        )
