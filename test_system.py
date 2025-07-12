#!/usr/bin/env python3
"""
Test script for Voice Conversational Agentic AI system
"""

import asyncio
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {str(e)}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint"""
    print("🔍 Testing chat endpoint...")
    try:
        data = {
            "message": "Hello, how are you?",
            "conversation_id": None
        }
        response = requests.post(
            "http://localhost:8000/api/v1/chat",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat endpoint working")
            print(f"   Response: {result['message'][:100]}...")
            print(f"   Conversation ID: {result['conversation_id']}")
            return True
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat endpoint error: {str(e)}")
        return False

def test_document_upload():
    """Test document upload"""
    print("🔍 Testing document upload...")
    try:
        # Create a test document
        test_content = """
        This is a test document for the Voice Conversational Agentic AI system.
        
        The system supports:
        - Real-time voice conversations
        - Text-based chat
        - Document upload and RAG
        - Conversation history
        
        This document will be used to test the RAG functionality.
        """
        
        # Save test document
        with open("test_document.txt", "w") as f:
            f.write(test_content)
        
        # Upload document
        with open("test_document.txt", "rb") as f:
            files = {"files": ("test_document.txt", f, "text/plain")}
            response = requests.post(
                "http://localhost:8000/api/v1/upload-documents",
                files=files
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document upload working")
            print(f"   Files processed: {result['files_processed']}")
            print(f"   Documents added: {result['documents_added']}")
            return True
        else:
            print(f"❌ Document upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Document upload error: {str(e)}")
        return False
    finally:
        # Clean up test file
        if os.path.exists("test_document.txt"):
            os.remove("test_document.txt")

def test_rag_functionality():
    """Test RAG functionality"""
    print("🔍 Testing RAG functionality...")
    try:
        # Test chat with RAG context
        data = {
            "message": "What does the test document say about the system?",
            "conversation_id": None
        }
        response = requests.post(
            "http://localhost:8000/api/v1/chat",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RAG functionality working")
            print(f"   Response: {result['message'][:100]}...")
            if result.get('context_used'):
                print("   RAG context was used")
            return True
        else:
            print(f"❌ RAG functionality failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ RAG functionality error: {str(e)}")
        return False

def test_conversation_history():
    """Test conversation history"""
    print("🔍 Testing conversation history...")
    try:
        # Get conversations
        response = requests.get("http://localhost:8000/api/v1/conversations")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Conversation history working")
            print(f"   Conversations found: {len(result['conversations'])}")
            return True
        else:
            print(f"❌ Conversation history failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conversation history error: {str(e)}")
        return False

def test_stats_endpoint():
    """Test stats endpoint"""
    print("🔍 Testing stats endpoint...")
    try:
        response = requests.get("http://localhost:8000/api/v1/stats")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Stats endpoint working")
            print(f"   RAG documents: {result['rag']['total_documents']}")
            print(f"   Conversations: {result['conversations']['total']}")
            return True
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats endpoint error: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Voice Conversational Agentic AI System Tests")
    print("=" * 60)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Chat Endpoint", test_chat_endpoint),
        ("Document Upload", test_document_upload),
        ("RAG Functionality", test_rag_functionality),
        ("Conversation History", test_conversation_history),
        ("Stats Endpoint", test_stats_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    print("\n🌐 Web Interface: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔊 WebSocket Endpoint: ws://localhost:8000/ws/voice")

if __name__ == "__main__":
    asyncio.run(main()) 