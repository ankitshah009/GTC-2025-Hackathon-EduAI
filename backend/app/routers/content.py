from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.models.schemas import ContentRequest, ContentResponse, ErrorResponse
from app.services.content_service import ContentService
from config.settings import get_settings
from typing import Dict, Any
import json
import asyncio

router = APIRouter()

@router.post("/generate", response_model=ContentResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def generate_content(request: ContentRequest, settings=Depends(get_settings)):
    """
    Generate educational content based on a topic and audience level.
    
    - **topic**: Educational topic to generate content for (e.g., "photosynthesis")
    - **audience**: Target audience level (elementary, middle school, high school, college, graduate)
    
    Returns:
    - **explanation**: Educational text explanation in markdown format
    - **image_prompts**: List of image prompts for visual representations
    """
    try:
        # Initialize content service
        content_service = ContentService(settings)
        
        # Generate content
        result = await content_service.generate_educational_content(
            topic=request.topic,
            audience=request.audience
        )
        
        return result
    except Exception as e:
        # Log the error (in a real app, you'd use proper logging)
        print(f"Error generating content: {str(e)}")
        
        # Return a user-friendly error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate educational content. Please try again."
        )

@router.post("/generate/stream")
async def generate_content_stream(request: ContentRequest, settings=Depends(get_settings)):
    """
    Stream educational content generation based on a topic and audience level.
    
    - **topic**: Educational topic to generate content for (e.g., "photosynthesis")
    - **audience**: Target audience level (elementary, middle school, high school, college, graduate)
    
    Returns:
    - A streaming response with chunks of the generated content
    """
    try:
        # Log the incoming request for debugging
        print(f"Received streaming request for topic: {request.topic}, audience: {request.audience}")
        
        # Initialize content service
        content_service = ContentService(settings)
        
        async def event_generator():
            """Generate server-sent events"""
            try:
                print("Starting content generation stream")
                async for chunk in content_service.generate_educational_content_stream(
                    topic=request.topic,
                    audience=request.audience
                ):
                    # Format as server-sent event
                    event_data = json.dumps(chunk)
                    yield f"data: {event_data}\n\n"
                    
                    # Small delay to prevent flooding
                    await asyncio.sleep(0.01)
                print("Stream completed successfully")
            except Exception as e:
                print(f"Streaming error: {str(e)}")
                error_data = {"error": f"Streaming failed: {str(e)}"}
                yield f"data: {json.dumps(error_data)}\n\n"
        
        # Set headers required for SSE
        headers = {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Prevents proxy buffering for Nginx
        }
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers=headers
        )
        
    except Exception as e:
        # Log the error
        print(f"Error setting up content stream: {str(e)}")
        
        # Return a user-friendly error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set up content stream. Please try again."
        )
