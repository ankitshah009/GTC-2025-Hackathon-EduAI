from config.settings import Settings
from app.nvidia_api.llm_client import LLMClient
from typing import Dict, List, Any, AsyncGenerator
import json
import re
import asyncio

class ContentService:
    """Service for educational content generation"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm_client = LLMClient(settings)
        
    async def generate_educational_content(self, topic: str, audience: str) -> Dict[str, Any]:
        """
        Generate educational content based on a topic and audience level.
        
        Args:
            topic: Educational topic to generate content for
            audience: Target audience level
            
        Returns:
            Dictionary containing the explanation and image prompts
        """
        if self.settings.USE_MOCK_DATA:
            # For development/demo, return mock data
            return self._generate_mock_content(topic, audience)
        
        # Construct prompt for the LLM
        prompt = self._create_content_prompt(topic, audience)
        
        # Call the LLM API
        response = await self.llm_client.generate_text(prompt)
        
        # Parse the response to extract explanation and image prompts
        explanation, image_prompts = self._parse_llm_response(response, topic, audience)
        
        return {
            "explanation": explanation,
            "image_prompts": image_prompts
        }
    
    async def generate_educational_content_stream(self, topic: str, audience: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate educational content with streaming responses.
        
        Args:
            topic: Educational topic to generate content for
            audience: Target audience level
            
        Yields:
            Dictionary containing chunks of the explanation
        """
        if self.settings.USE_MOCK_DATA:
            # For development/demo, yield mock data in chunks
            mock_content = self._generate_mock_content(topic, audience)
            explanation = mock_content["explanation"]
            
            # Split mock explanation into chunks to simulate streaming
            chunk_size = 20
            chunks = [explanation[i:i+chunk_size] for i in range(0, len(explanation), chunk_size)]
            
            for chunk in chunks:
                yield {"chunk": chunk, "finished": False}
                await asyncio.sleep(0.1)  # Simulate delay between chunks
                
            # Finally yield the image prompts
            yield {
                "chunk": "",
                "finished": True,
                "image_prompts": mock_content["image_prompts"]
            }
            return
        
        # Construct prompt for the LLM
        prompt = self._create_content_prompt(topic, audience)
        
        # Call the LLM API with streaming
        collected_text = ""
        
        async for chunk in self.llm_client.generate_text_stream(prompt):
            collected_text += chunk
            yield {"chunk": chunk, "finished": False}
        
        # Parse the complete response to extract explanation and image prompts
        explanation, image_prompts = self._parse_llm_response(collected_text, topic, audience)
        
        # Final yield with image prompts
        yield {
            "chunk": "",
            "finished": True,
            "image_prompts": image_prompts
        }
    
    def _create_content_prompt(self, topic: str, audience: str) -> str:
        """Create a prompt for the LLM to generate educational content"""
        return f"""
        Generate an educational lesson on {topic} for {audience} level students.
        
        The response should include:
        1. A detailed text explanation in markdown format with:
           - A title and introduction
           - Main concepts clearly explained at appropriate level for {audience} students
           - Deeper understanding section that connects {topic} to other areas of study
        
        2. A separate section titled "IMAGE_PROMPTS" containing exactly 3 detailed image prompts 
           that would be useful to illustrate key concepts from this lesson. Each prompt should
           be on a new line starting with "- " and be appropriate for the {audience} level.
        
        Format the response with markdown for headings and structure.
        """
    
    def _parse_llm_response(self, response: str, topic: str, audience: str) -> tuple:
        """
        Parse the LLM response to extract explanation and image prompts.
        
        Args:
            response: Raw response from the LLM
            topic: Original topic (for fallback)
            audience: Original audience (for fallback)
            
        Returns:
            Tuple of (explanation, image_prompts)
        """
        try:
            # Split the response to extract explanation and image prompts
            parts = response.split("IMAGE_PROMPTS")
            
            explanation = parts[0].strip()
            
            # Extract image prompts if available
            image_prompts = []
            if len(parts) > 1:
                prompt_text = parts[1].strip()
                # Extract bullet points
                image_prompts = [line.strip()[2:].strip() for line in prompt_text.split('\n') 
                                if line.strip().startswith('- ')]
            
            # If no image prompts were found, generate default ones
            if not image_prompts or len(image_prompts) < 3:
                image_prompts = [
                    f"Educational diagram showing the process of {topic} for {audience} students",
                    f"Visual representation of key concepts in {topic} appropriate for {audience} level",
                    f"Illustrative example of {topic} in action for {audience} understanding"
                ]
            
            return explanation, image_prompts[:3]  # Limit to 3 prompts
            
        except Exception as e:
            # If parsing fails, return a default structure
            print(f"Error parsing LLM response: {str(e)}")
            default_explanation = f"""
            # {topic.capitalize()} (for {audience})
            
            ## Introduction
            {topic} is a fascinating concept that is important to understand at the {audience} level.
            
            ## Main Concepts
            When studying {topic}, it's important to understand the key principles involved.
            
            ## Deeper Understanding
            At the {audience} level, students should begin to grasp how {topic} connects to other areas of study.
            """
            
            default_image_prompts = [
                f"Educational diagram showing the process of {topic} for {audience} students",
                f"Visual representation of key concepts in {topic} appropriate for {audience} level",
                f"Illustrative example of {topic} in action for {audience} understanding"
            ]
            
            return default_explanation, default_image_prompts
    
    def _generate_mock_content(self, topic: str, audience: str) -> Dict[str, Any]:
        """Generate mock content for development and testing"""
        explanation = f"""
# {topic.capitalize()} (for {audience})

## Introduction
{topic} is a fascinating concept that is important to understand at the {audience} level. 
This educational content is tailored specifically for {audience} students.

## Main Concepts
When studying {topic}, it's important to understand the key principles involved:
- First principle of {topic}
- Second principle of {topic}
- Applications of {topic} in real world scenarios

## Deeper Understanding
At the {audience} level, students should begin to grasp how {topic} connects to other areas of study.
        """
        
        image_prompts = [
            f"Educational diagram showing the process of {topic} for {audience} students",
            f"Visual representation of key concepts in {topic} appropriate for {audience} level",
            f"Illustrative example of {topic} in action for {audience} understanding"
        ]
        
        return {
            "explanation": explanation,
            "image_prompts": image_prompts
        }
