#!/usr/bin/env python3
"""
Debug script for WebSocket testing
"""

import asyncio
import websockets
import json
import time

async def test_websocket_debug():
    """Test WebSocket communication with detailed logging"""
    
    uri = 'ws://localhost:8000/ws/voice'
    
    try:
        print("🔌 Connecting to WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully")
            
            # Wait for connection message
            print("📥 Waiting for connection message...")
            connection_msg = await websocket.recv()
            print(f"📨 Connection message: {connection_msg}")
            
            # Wait a moment
            await asyncio.sleep(1)
            
            # Send ping
            print("📤 Sending ping...")
            await websocket.send(json.dumps({'type': 'ping'}))
            
            # Wait for pong
            print("📥 Waiting for pong...")
            pong_msg = await websocket.recv()
            print(f"📨 Pong message: {pong_msg}")
            
            # Wait a moment
            await asyncio.sleep(1)
            
            # Send text message
            print("📤 Sending text message...")
            text_msg = {
                'type': 'text',
                'text': 'Hello, how are you?',
                'conversation_id': None
            }
            await websocket.send(json.dumps(text_msg))
            
            # Wait for response
            print("📥 Waiting for text response...")
            response = await websocket.recv()
            print(f"📨 Text response: {response}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket_debug()) 