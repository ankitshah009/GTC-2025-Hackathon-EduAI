from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Union

class ContentRequest(BaseModel):
    """Request model for educational content generation"""
    topic: str = Field(..., description="Educational topic to generate content for")
    audience: str = Field(..., description="Target audience level (elementary, middle school, high school, college, graduate)")
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "photosynthesis",
                "audience": "high school"
            }
        }

class ImagePrompt(BaseModel):
    """Model for an image prompt"""
    prompt: str = Field(..., description="Text prompt for image generation")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Educational diagram showing the process of photosynthesis for high school students"
            }
        }

class ContentResponse(BaseModel):
    """Response model for educational content"""
    explanation: str = Field(..., description="Educational text explanation in markdown format")
    image_prompts: List[str] = Field(..., description="List of image prompts for visual representations")
    
    class Config:
        schema_extra = {
            "example": {
                "explanation": "# Photosynthesis (for high school)\n\n## Introduction\nPhotosynthesis is a process used by plants...",
                "image_prompts": [
                    "Educational diagram showing the process of photosynthesis for high school students",
                    "Visual representation of key concepts in photosynthesis appropriate for high school level"
                ]
            }
        }

class ContentStreamChunk(BaseModel):
    """Model for a chunk of the streaming content response"""
    chunk: str = Field(..., description="A chunk of the generated text")
    finished: bool = Field(..., description="Flag indicating if this is the final chunk")
    image_prompts: Optional[List[str]] = Field(None, description="List of image prompts (only included in final chunk)")
    
    class Config:
        schema_extra = {
            "example": {
                "chunk": "# Photosynthesis (for high school)\n\n",
                "finished": False,
                "image_prompts": None
            }
        }

class ImageGenerationRequest(BaseModel):
    """Request model for image generation"""
    prompt: str = Field(..., description="Text prompt for image generation")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Educational diagram showing the process of photosynthesis for high school students"
            }
        }

class ImageResponse(BaseModel):
    """Response model for image generation"""
    image_url: str = Field(..., description="URL to the generated image")
    
    class Config:
        schema_extra = {
            "example": {
                "image_url": "https://example.com/generated-image.jpg"
            }
        }

class GeminiImageResponse(BaseModel):
    """Response model for Gemini image generation"""
    success: bool = Field(..., description="Flag indicating if the image generation was successful")
    image_url: Optional[str] = Field(None, description="URL to the generated image (if successful)")
    error: Optional[str] = Field(None, description="Error message (if failed)")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "image_url": "https://example.com/generated-image.jpg",
                "error": None
            }
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Failed to generate content. Please try again."
            }
        }
