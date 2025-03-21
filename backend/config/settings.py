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
    CORS_ORIGINS: List[str] = ["*"]
    
    # LLM API settings
    LLM_API_TYPE: str = "openai"  # "openai" or "openai_compatible"
    LLM_API_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    LLM_API_KEY: Optional[str] = None
    
    # LLM model settings
    LLM_MODEL_ID: str = "nvidia/llama-3.3-nemotron-super-49b-v1"
    LLM_TEMPERATURE: float = 0.6
    LLM_TOP_P: float = 0.95
    LLM_MAX_TOKENS: int = 4096
    LLM_FREQUENCY_PENALTY: float = 0
    LLM_PRESENCE_PENALTY: float = 0
    LLM_STREAM: bool = False  # Set to True for streaming responses in async handlers
    
    # System message for the model
    LLM_SYSTEM_MESSAGE: str = "You are an educational AI assistant designed to create high-quality content for students at various academic levels. Provide detailed and accurate information."
    
    # Text-to-image model settings
    IMAGE_MODEL_ID: str = "stable-diffusion-xl"
    IMAGE_SIZE: str = "1024x1024"
    
    # Cache settings
    CONTENT_CACHE_TTL: int = 3600  # Cache TTL in seconds (1 hour)
    
    # Mock mode for development
    USE_MOCK_DATA: bool = True  # Will use mock data even if API key is provided
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get application settings, cached to avoid reloading from disk"""
    return Settings()
