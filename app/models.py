"""
Pydantic models for Voice Conversational Agentic AI
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for text chat"""
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")


class ChatResponse(BaseModel):
    """Response model for text chat"""
    message: str = Field(..., description="AI response message")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: datetime = Field(default_factory=datetime.now)
    context_used: Optional[List[str]] = Field(None, description="RAG context used")


class VoiceMessage(BaseModel):
    """WebSocket voice message model"""
    type: str = Field(..., description="Message type")
    data: Optional[str] = Field(None, description="Base64 encoded audio data")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    text: Optional[str] = Field(None, description="Transcribed text")


class VoiceResponse(BaseModel):
    """WebSocket voice response model"""
    type: str = Field(..., description="Response type")
    text: str = Field(..., description="AI response text")
    audio: Optional[str] = Field(None, description="Base64 encoded audio response")
    conversation_id: str = Field(..., description="Conversation ID")
    timestamp: datetime = Field(default_factory=datetime.now)


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    message: str = Field(..., description="Upload status message")
    files_processed: int = Field(..., description="Number of files processed")
    documents_added: int = Field(..., description="Number of documents added to RAG")
    errors: Optional[List[str]] = Field(None, description="List of errors if any")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = Field(..., description="API version")


class ConversationHistory(BaseModel):
    """Conversation history model"""
    conversation_id: str = Field(..., description="Conversation ID")
    messages: List[Dict[str, Any]] = Field(..., description="List of messages")
    created_at: datetime = Field(..., description="Conversation creation time")
    updated_at: datetime = Field(..., description="Last update time")


class RAGDocument(BaseModel):
    """RAG document model"""
    id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Original filename")
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    created_at: datetime = Field(default_factory=datetime.now) 