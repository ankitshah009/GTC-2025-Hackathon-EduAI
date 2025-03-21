from fastapi import APIRouter, Depends, HTTPException
from app.models.deep_research_schemas import DeepResearchRequest, DeepResearchResponse
from app.models.schemas import ErrorResponse
from app.services.deep_research_service import DeepResearchService
from config.settings import get_settings
from typing import Dict, Any

router = APIRouter()

@router.post("/research", response_model=DeepResearchResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def deep_research(request: DeepResearchRequest, settings=Depends(get_settings)):
    """
    Perform deep research on an educational topic.
    
    - **topic**: Main educational topic to research
    - **subtopics**: Optional list of specific subtopics to focus on
    - **academic_level**: Academic level (e.g., high school, undergraduate, graduate)
    - **include_references**: Whether to include academic references
    
    Returns a comprehensive research response including:
    - Introduction
    - Content sections
    - Academic references (if requested)
    - Related topics
    - Key concepts
    - Visualization prompts
    """
    try:
        # Initialize research service
        research_service = DeepResearchService(settings)
        
        # Generate research content
        result = await research_service.generate_research(
            topic=request.topic,
            subtopics=request.subtopics,
            academic_level=request.academic_level,
            include_references=request.include_references
        )
        
        return result
    except Exception as e:
        # Log the error (in a real app, you'd use proper logging)
        print(f"Error generating deep research: {str(e)}")
        
        # Return a user-friendly error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate research content. Please try again."
        )

@router.get("/trending-topics", responses={500: {"model": ErrorResponse}})
async def get_trending_topics(academic_level: str = "college", limit: int = 10, settings=Depends(get_settings)):
    """
    Get trending educational topics for research.
    
    - **academic_level**: Academic level filter (e.g., high school, undergraduate, graduate)
    - **limit**: Maximum number of topics to return
    
    Returns a list of trending educational topics suitable for deep research.
    """
    try:
        # Initialize research service
        research_service = DeepResearchService(settings)
        
        # Get trending topics
        topics = await research_service.get_trending_topics(
            academic_level=academic_level,
            limit=limit
        )
        
        return {"topics": topics}
    except Exception as e:
        # Log the error
        print(f"Error fetching trending topics: {str(e)}")
        
        # Return a user-friendly error
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch trending topics. Please try again."
        )
