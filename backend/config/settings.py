import os
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List, Union
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "EduAI"
    APP_DESCRIPTION: str = "AI-Powered Educational Content Generator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS settings
    CORS_ORIGINS: Union[List[str], str] = ["*"]
    
    # LLM API settings
    LLM_API_TYPE: str = "openai"  # "openai" or "openai_compatible"
    LLM_API_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    LLM_API_KEY: Optional[str] = None
    
    # NVIDIA API settings
    NVIDIA_API_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_API_KEY: Optional[str] = None
    
    # Google Gemini API settings
    GEMINI_API_KEY: Optional[str] = None
    
    # LLM model settings
    LLM_MODEL_ID: str = "nvidia/llama-3.3-nemotron-super-49b-v1"
    LLM_TEMPERATURE: float = 0.7  # Slightly increase for more creative output
    LLM_TOP_P: float = 0.9
    LLM_MAX_TOKENS: int = 4096
    LLM_FREQUENCY_PENALTY: float = 0.1  # Add slight penalty to avoid repetitive text
    LLM_PRESENCE_PENALTY: float = 0.1  # Add slight penalty to encourage diverse topics
    LLM_STREAM: bool = False  # Set to True for streaming responses in async handlers
    
    # System message for the model
    LLM_SYSTEM_MESSAGE: str = """You are an expert educational AI assistant designed to create high-quality, 
    detailed, and thoughtful educational content. Your explanations should be comprehensive, accurate, 
    and demonstrate deep reasoning appropriate for the target audience level. Include real-world examples, 
    historical context when relevant, and connections to related concepts."""
    
    # Text-to-image model settings
    IMAGE_MODEL_ID: str = "stable-diffusion-xl"
    IMAGE_SIZE: str = "1024x1024"
    
    # File paths
    STATIC_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
    
    # Cache settings
    CONTENT_CACHE_TTL: int = 3600  # Cache TTL in seconds (1 hour)
    
    # Mock mode for development
    USE_MOCK_DATA: bool = False  # Set to False to use the real API instead of mock data
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Ensure the static directory exists
        os.makedirs(self.STATIC_DIR, exist_ok=True)
        
        # Use NVIDIA_API_KEY if LLM_API_KEY is not provided
        if not self.LLM_API_KEY and self.NVIDIA_API_KEY:
            self.LLM_API_KEY = self.NVIDIA_API_KEY

@lru_cache()
def get_settings() -> Settings:
    """Get application settings, cached to avoid reloading from disk"""
    return Settings()
