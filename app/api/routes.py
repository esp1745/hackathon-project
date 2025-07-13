"""
API routes for Voice Conversational Agentic AI
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
import json
import uuid
from datetime import datetime

from app.models import (
    ChatRequest, 
    ChatResponse, 
    DocumentUploadResponse, 
    HealthResponse
)
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.conversation_service import ConversationService
from app.services.speech_service import SpeechService
from app.config import settings

router = APIRouter()

# Initialize services
conversation_service = ConversationService()
llm_service = LLMService()
rag_service = RAGService()
speech_service = SpeechService()

@router.get("/")
async def read_root():
    """Serve the main HTML page"""
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="voice-conversational-ai",
        version="1.0.0"
    )

@router.post("/api/v1/chat")
async def chat_endpoint(request: Dict[str, Any]):
    """Chat endpoint for text-based conversations"""
    try:
        message = request.get("message", "")
        conversation_id = request.get("conversation_id")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get conversation history
        conversation_history = []
        if conversation_id:
            conversation_history = conversation_service.get_conversation_history(conversation_id)
        
        # Get RAG context
        rag_context = await rag_service.get_context_for_query(message)
        
        # Generate response
        response = await llm_service.generate_response(
            message=message,
            conversation_history=conversation_history,
            rag_context=rag_context
        )
        
        # Save conversation
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        conversation_service.add_message(conversation_id, "user", message)
        conversation_service.add_message(conversation_id, "assistant", response)
        
        return {
            "response": response,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload document for RAG processing"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Save file
        file_path = f"data/documents/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process document
        await rag_service.add_document(content.decode('utf-8'), file.filename)
        
        return {
            "message": f"Document {file.filename} uploaded and processed successfully",
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/conversations")
async def get_conversations():
    """Get all conversations"""
    try:
        conversations = conversation_service.list_conversations()
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get specific conversation"""
    try:
        conversation = conversation_service.get_conversation_summary(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/v1/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation"""
    try:
        conversation_service.delete_conversation(conversation_id)
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/stats")
async def get_stats():
    """Get system statistics"""
    try:
        conversations = conversation_service.list_conversations()
        stats = {
            "total_conversations": len(conversations),
            "total_messages": sum(len(conv.get("message_count", 0)) for conv in conversations),
            "system_status": "healthy"
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 