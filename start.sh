#!/bin/bash

# Voice Conversational Agentic AI Startup Script

echo "🚀 Starting Voice Conversational Agentic AI System"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your OpenAI API key and other settings."
    echo "   You can get an API key from: https://platform.openai.com/api-keys"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/documents
mkdir -p data/conversations
mkdir -p chroma_db
mkdir -p static

# Check if static files exist
if [ ! -f "static/index.html" ]; then
    echo "📄 Creating web interface..."
    # The HTML file should already exist from our previous creation
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 To start the server, run:"
echo "   python main.py"
echo ""
echo "🔧 To run in development mode:"
echo "   python main.py --reload"
echo ""
echo "🧪 To test the system:"
echo "   python test_system.py"
echo ""
echo "📚 API Documentation will be available at:"
echo "   http://localhost:8000/docs"
echo ""
echo "🎤 Web Interface will be available at:"
echo "   http://localhost:8000"
echo ""
echo "🔊 WebSocket Voice Endpoint:"
echo "   ws://localhost:8000/ws/voice" 