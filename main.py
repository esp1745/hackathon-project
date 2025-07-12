#!/usr/bin/env python3
"""
Voice Conversational Agentic AI with RAG
Main application entry point
"""

import uvicorn
import argparse
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.routes import router
from app.api.websocket import websocket_router

# Load environment variables
load_dotenv()
print("DEBUG: OPENAI_API_KEY =", os.environ.get("OPENAI_API_KEY"))

# Create FastAPI app
app = FastAPI(
    title="Voice Conversational Agentic AI",
    description="A Python-based RESTful API system for real-time voice conversations with LLM and RAG",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")
app.include_router(websocket_router)

# Mount static files for document uploads
os.makedirs("data/documents", exist_ok=True)
app.mount("/documents", StaticFiles(directory="data/documents"), name="documents")

# Mount static files for web client
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Root endpoint - redirect to web client"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "voice-conversational-ai"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice Conversational Agentic AI")
    parser.add_argument("--host", default=settings.HOST, help="Host to bind to")
    parser.add_argument("--port", type=int, default=settings.PORT, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    print(f"🚀 Starting Voice Conversational Agentic AI...")
    print(f"📡 Server will be available at: http://{args.host}:{args.port}")
    print(f"📚 API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔊 WebSocket Voice Endpoint: ws://{args.host}:{args.port}/ws/voice")
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info" if args.debug else "warning"
    ) 