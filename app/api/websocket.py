"""
WebSocket handlers for real-time voice conversations
"""

import json
import base64
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from app.models import VoiceMessage, VoiceResponse
from app.services.speech_service import speech_service
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.services.conversation_service import conversation_service


websocket_router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new client"""
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        """Disconnect a client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(message))


# Create global connection manager
manager = ConnectionManager()


@websocket_router.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice conversations
    """
    client_id = None
    
    try:
        # Accept the WebSocket connection
        await websocket.accept()
        
        # Generate client ID
        client_id = f"client_{len(manager.active_connections) + 1}"
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection",
            "client_id": client_id,
            "message": "Connected to voice conversation service"
        }))
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            print(f"[WebSocket] Received message: {message_data}")
            
            # Handle ping/pong for testing
            if message_data.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                continue
            
            # Validate message format
            try:
                message = VoiceMessage(**message_data)
                print(f"[WebSocket] Message validated: type={message.type}")
            except Exception as e:
                print(f"[WebSocket] Message validation error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Invalid message format: {str(e)}"
                }))
                continue
            
            # Handle different message types
            if message.type == "audio_data":
                print("[WebSocket] Handling audio message")
                await handle_audio_message(websocket, message, client_id)
            elif message.type == "text":
                print("[WebSocket] Handling text message")
                await handle_text_message(websocket, message, client_id)
            else:
                print(f"[WebSocket] Unknown message type: {message.type}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message.type}"
                }))
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"WebSocket error: {str(e)}"
            }))
        except:
            pass


async def handle_audio_message(websocket: WebSocket, message: VoiceMessage, client_id: str):
    """
    Handle audio data message
    """
    try:
        # Get or create conversation ID
        conversation_id = message.conversation_id
        if not conversation_id:
            conversation_id = conversation_service.create_conversation()
        
        # Convert base64 audio to bytes
        if not message.data:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "No audio data provided"
            }))
            return
            
        audio_data = speech_service.base64_to_audio(message.data)
        
        # Validate audio format
        if not speech_service.validate_audio_format(audio_data):
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Invalid audio format"
            }))
            return
        
        # Convert speech to text
        transcribed_text = await speech_service.speech_to_text(audio_data)
        
        if not transcribed_text.strip():
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Could not transcribe audio"
            }))
            return
        
        # Get conversation history
        conversation_history = conversation_service.get_conversation_context(conversation_id)
        
        # Get RAG context for the query
        rag_context = await rag_service.get_context_for_query(transcribed_text)
        
        # Generate response using LLM
        response_text = await llm_service.generate_response(
            message=transcribed_text,
            conversation_history=conversation_history,
            rag_context=rag_context
        )
        
        # Convert response to speech
        audio_response = await speech_service.text_to_speech(response_text)
        audio_base64 = speech_service.audio_to_base64(audio_response)
        
        # Add messages to conversation
        conversation_service.add_message(
            conversation_id=conversation_id,
            role="user",
            content=transcribed_text,
            metadata={"source": "voice", "audio_length": len(audio_data)}
        )
        
        conversation_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
            metadata={
                "source": "voice",
                "rag_context_used": bool(rag_context),
                "audio_length": len(audio_response)
            }
        )
        
        # Send response
        response = VoiceResponse(
            type="response",
            text=response_text,
            audio=audio_base64,
            conversation_id=conversation_id
        )
        
        await websocket.send_text(response.json())
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Error processing audio: {str(e)}"
        }))


async def handle_text_message(websocket: WebSocket, message: VoiceMessage, client_id: str):
    """
    Handle text message (for debugging/testing)
    """
    try:
        # Get or create conversation ID
        conversation_id = message.conversation_id
        if not conversation_id:
            conversation_id = conversation_service.create_conversation()
        
        # Get conversation history
        conversation_history = conversation_service.get_conversation_context(conversation_id)
        
        # Get RAG context for the query
        if not message.text:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "No text provided"
            }))
            return
            
        rag_context = await rag_service.get_context_for_query(message.text)
        
        # Generate response using LLM
        response_text = await llm_service.generate_response(
            message=message.text,
            conversation_history=conversation_history,
            rag_context=rag_context
        )
        
        # Convert response to speech
        audio_response = await speech_service.text_to_speech(response_text)
        audio_base64 = speech_service.audio_to_base64(audio_response)
        
        # Add messages to conversation
        conversation_service.add_message(
            conversation_id=conversation_id,
            role="user",
            content=message.text,
            metadata={"source": "text"}
        )
        
        conversation_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text,
            metadata={
                "source": "text",
                "rag_context_used": bool(rag_context)
            }
        )
        
        # Send response
        response = VoiceResponse(
            type="response",
            text=response_text,
            audio=audio_base64,
            conversation_id=conversation_id
        )
        
        await websocket.send_text(response.json())
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Error processing text: {str(e)}"
        })) 