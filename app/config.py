"""
Configuration management for Voice Conversational Agentic AI
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    
    # Speech Recognition Configuration
    WHISPER_MODEL: str = "whisper-1"
    
    # Text-to-Speech Configuration
    TTS_MODEL: str = "tts-1"
    TTS_VOICE: str = "alloy"
    
    # RAG Configuration
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Audio Configuration
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHANNELS: int = 1
    AUDIO_CHUNK_SIZE: int = 1024
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = [".txt", ".pdf", ".docx", ".md", ".csv"]
    
    # Conversation Configuration
    MAX_CONVERSATION_HISTORY: int = 50
    CONVERSATION_TIMEOUT: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings() 