# Voice Conversational Agentic AI with RAG

A Python-based RESTful API system for real-time two-way voice conversations with a Large Language Model (LLM), featuring Retrieval-Augmented Generation (RAG) capabilities and real estate data integration.

## 🚀 Features

- **Real-time Voice Conversations**: WebSocket-based voice communication
- **Speech-to-Text**: OpenAI Whisper API integration
- **Text-to-Speech**: OpenAI TTS for natural voice responses
- **RAG (Retrieval-Augmented Generation)**: Context-aware responses using ChromaDB
- **Real Estate Knowledge Base**: Specialized CSV data processing
- **Modern Web Interface**: Beautiful UI for voice and text interactions
- **Conversation Memory**: Persistent conversation history
- **Document Upload**: Support for CSV and other document formats

## 🏗️ Architecture

```
├── app/
│   ├── api/                 # FastAPI routes and WebSocket handlers
│   ├── services/            # Core business logic
│   │   ├── llm_service.py  # OpenAI GPT-4 integration
│   │   ├── speech_service.py # Speech-to-text and text-to-speech
│   │   ├── rag_service.py  # RAG with ChromaDB
│   │   └── conversation_service.py # Conversation management
│   ├── utils/              # Utility functions
│   └── config.py           # Configuration settings
├── static/                 # Web interface files
├── data/                   # Data storage
└── main.py                 # FastAPI application entry point
```

## 📋 Prerequisites

- Python 3.12+
- ffmpeg (for audio processing)
- OpenAI API key

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/esp1745/hackathon-project.git
   cd hackathon-project
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install ffmpeg:**
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # Fedora
   sudo dnf install ffmpeg
   ```

5. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your OpenAI API key
   ```

## 🚀 Quick Start

1. **Start the server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --env-file .env
   ```

2. **Upload your CSV dataset:**
   ```bash
   python upload_csv_dataset.py
   ```

3. **Access the web interface:**
   - Open `http://localhost:8000` in your browser
   - Start voice or text conversations

## 📡 API Endpoints

### REST API
- `GET /health` - Health check
- `POST /api/v1/chat` - Text chat
- `POST /api/v1/upload-documents` - Upload documents
- `GET /api/v1/conversations` - List conversations
- `GET /api/v1/stats` - System statistics

### WebSocket
- `WS /ws/voice` - Real-time voice conversations

## 🎯 Usage Examples

### Voice Conversation
1. Open the web interface
2. Click the microphone button
3. Speak your question
4. Receive voice response

### Text Chat
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What properties are in the database?", "conversation_id": null}'
```

### WebSocket Voice
```python
import asyncio
import websockets
import json

async def voice_chat():
    uri = 'ws://localhost:8000/ws/voice'
    async with websockets.connect(uri) as websocket:
        # Send voice message
        await websocket.send(json.dumps({
            'type': 'audio_data',
            'data': 'base64_encoded_audio',
            'conversation_id': None
        }))
        response = await websocket.recv()
        print(response)

asyncio.run(voice_chat())
```

## 📊 Real Estate Data Features

The system includes specialized processing for real estate CSV data:

- **Property Information**: Addresses, floors, suites, sizes
- **Financial Data**: Rent per SF, annual/monthly rent, GCI
- **Broker Information**: Associates, email IDs
- **Market Analysis**: Property comparisons and insights

### CSV Format Support
The system automatically processes CSV files with columns like:
- Property Address
- Floor/Suite
- Size (SF)
- Rent per SF per Year
- Associates
- Broker Email ID
- Annual/Monthly Rent
- GCI (3 years)

## 🔧 Configuration

Edit `app/config.py` to customize:
- OpenAI API settings
- Whisper model selection
- TTS voice preferences
- RAG parameters
- Database settings

## 🧪 Testing

### Test Questions
Try these questions to test different features:

1. **Basic Functionality**: "Hello, how are you?"
2. **RAG Queries**: "What properties are in the database?"
3. **Market Analysis**: "What's the average property price?"
4. **Broker Info**: "Who are the top brokers?"
5. **Property Details**: "Tell me about properties in New York"

### Test Scripts
- `test_websocket_debug.py` - WebSocket testing
- `upload_csv_dataset.py` - Dataset upload testing

## 🛡️ Security

- Environment variable protection for API keys
- Input validation and sanitization
- Error handling and logging
- CORS configuration for web interface

## 📈 Performance

- Async/await for non-blocking operations
- Efficient audio processing with ffmpeg
- Optimized RAG queries with ChromaDB
- WebSocket for real-time communication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- OpenAI for GPT-4, Whisper, and TTS APIs
- FastAPI for the web framework
- ChromaDB for vector storage
- Pydub for audio processing

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the logs for debugging information
- Ensure ffmpeg is properly installed
- Verify OpenAI API key configuration

---

**Happy Voice Conversing! 🎤✨** 