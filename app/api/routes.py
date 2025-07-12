"""
API routes for Voice Conversational Agentic AI
"""

import os
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.models import (
    ChatRequest, 
    ChatResponse, 
    DocumentUploadResponse, 
    HealthResponse
)
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.conversation_service import conversation_service
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="voice-conversational-ai",
        version="1.0.0"
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Text-based chat endpoint with RAG enhancement
    """
    try:
        # Get or create conversation ID
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = conversation_service.create_conversation()
        
        # Get conversation history
        conversation_history = conversation_service.get_conversation_context(conversation_id)
        
        # Get RAG context for the query
        rag_context = await rag_service.get_context_for_query(request.message)
        
        # Generate response using LLM
        response_text = await llm_service.generate_response(
            message=request.message,
            conversation_history=conversation_history,
            rag_context=rag_context
        )
        
        # Add messages to conversation
        conversation_service.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        
        conversation_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
            metadata={"rag_context_used": bool(rag_context)}
        )
        
        return ChatResponse(
            message=response_text,
            conversation_id=conversation_id,
            context_used=rag_context if rag_context else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-documents", response_model=DocumentUploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload documents for RAG system
    """
    try:
        files_processed = 0
        documents_added = 0
        errors = []
        
        for file in files:
            try:
                # Validate file type
                if not file.filename:
                    errors.append("File has no filename")
                    continue
                    
                file_extension = os.path.splitext(file.filename)[1].lower()
                if file_extension not in settings.ALLOWED_FILE_TYPES:
                    errors.append(f"Unsupported file type: {file.filename}")
                    continue
                
                # Validate file size
                if file.size and file.size > settings.MAX_FILE_SIZE:
                    errors.append(f"File too large: {file.filename}")
                    continue
                
                # Read file content
                content = await file.read()
                
                # Convert to text (basic implementation - in production, use proper parsers)
                if file_extension == ".txt":
                    text_content = content.decode('utf-8')
                elif file_extension == ".md":
                    text_content = content.decode('utf-8')
                else:
                    # For other file types, try to decode as text
                    try:
                        text_content = content.decode('utf-8')
                    except UnicodeDecodeError:
                        errors.append(f"Could not decode file as text: {file.filename}")
                        continue
                
                # Add document to RAG system
                doc_id = await rag_service.add_document(
                    content=text_content,
                    filename=file.filename or "unknown"
                )
                
                files_processed += 1
                documents_added += 1
                
            except Exception as e:
                errors.append(f"Error processing {file.filename}: {str(e)}")
                continue
        
        return DocumentUploadResponse(
            message=f"Processed {files_processed} files, added {documents_added} documents",
            files_processed=files_processed,
            documents_added=documents_added,
            errors=errors if errors else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents():
    """
    List all documents in the RAG system
    """
    try:
        documents = await rag_service.list_documents()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    """
    Delete a document from the RAG system
    """
    try:
        deleted = await rag_service.delete_document(filename)
        if deleted:
            return {"message": f"Document {filename} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Document {filename} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def list_conversations():
    """
    List all conversations
    """
    try:
        conversations = conversation_service.list_conversations()
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get conversation history
    """
    try:
        messages = conversation_service.get_conversation_history(conversation_id)
        summary = conversation_service.get_conversation_summary(conversation_id)
        
        return {
            "conversation_id": conversation_id,
            "summary": summary,
            "messages": messages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation
    """
    try:
        deleted = conversation_service.delete_conversation(conversation_id)
        if deleted:
            return {"message": f"Conversation {conversation_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """
    Get system statistics
    """
    try:
        # Get RAG stats
        rag_stats = rag_service.get_collection_stats()
        
        # Get conversation stats
        conversations = conversation_service.list_conversations()
        conversation_count = len(conversations)
        
        # Clean up old conversations
        deleted_count = conversation_service.cleanup_old_conversations()
        
        return {
            "rag": rag_stats,
            "conversations": {
                "total": conversation_count,
                "cleaned_up": deleted_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 