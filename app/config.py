from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration settings.
    
    Configuration sections:
    - API settings (title, version, description)
    - ChatBet API connection (URL, timeout)
    - Google AI integration (API key, model)
    - Application behavior (debug, conversation limits)
    """
    api_title: str = "ChatBet AI Assistant"
    api_version: str = "1.0.0"
    api_description: str = "Intelligent conversational chatbot for sports betting"
    
    chatbet_api_base_url: str = "https://v46fnhvrjvtlrsmnismnwhdh5y0lckdl.lambda-url.us-east-1.on.aws"
    chatbet_api_timeout: int = 30
    
    google_ai_api_key: str
    google_ai_model: str = "gemini-1.5-flash"
    
    debug: bool = False
    max_conversation_history: int = 10
    conversation_timeout: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()