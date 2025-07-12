"""
Speech service for handling STT and TTS operations
"""

import base64
import io
import tempfile
import os
from typing import Optional, Tuple
import openai
from openai import OpenAI
import soundfile as sf
import numpy as np
from pydub import AudioSegment
from pydub.utils import make_chunks
import io
import base64
import tempfile
import os

from app.config import settings


class SpeechService:
    """Service for speech-to-text and text-to-speech operations"""
    
    def __init__(self):
        """Initialize the speech service"""
        # Check if we have a valid API key
        self.demo_mode = settings.OPENAI_API_KEY == "your_openai_api_key_here" or not settings.OPENAI_API_KEY
        print(f"[SpeechService] Initialized. DEMO_MODE={self.demo_mode}")
        if self.demo_mode:
            print("⚠️  Speech service running in DEMO MODE")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            print("[SpeechService] OpenAI client initialized.")
        self.whisper_model = settings.WHISPER_MODEL
        self.tts_model = settings.TTS_MODEL
        self.tts_voice = settings.TTS_VOICE
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        print(f"[SpeechService] speech_to_text called. Bytes length: {len(audio_data)}")
        if self.demo_mode:
            print("[SpeechService] DEMO_MODE: Returning demo transcript.")
            return "This is a demo transcript."
        try:
            # Convert any format to WAV using pydub
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            print(f"[SpeechService] Audio converted to WAV. Bytes length: {wav_io.getbuffer().nbytes}")

            if self.client is None:
                raise Exception("OpenAI client not initialized")

            # Pass the WAV audio to Whisper/OpenAI
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
                temp_audio_file.write(wav_io.read())
                temp_file_path = temp_audio_file.name
            print(f"[SpeechService] Temporary WAV file created: {temp_file_path}")

            with open(temp_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=self.whisper_model,
                    file=audio_file,
                    response_format="text"
                )
                print(f"[SpeechService] Transcription result: {transcript}")
            os.remove(temp_file_path)
            print(f"[SpeechService] Temporary WAV file deleted: {temp_file_path}")
            return transcript
        except Exception as e:
            print(f"[SpeechService] Error in speech_to_text: {e}")
            raise
    
    async def text_to_speech(self, text: str) -> bytes:
        print(f"[SpeechService] text_to_speech called. Text: {text}")
        """
        Convert text to speech using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio data in bytes
        """
        try:
            # Demo mode - return empty audio data
            if self.demo_mode:
                print("[SpeechService] Demo mode: returning silent audio.")
                # Return a minimal valid audio file (silence)
                return b'\x52\x49\x46\x46\x24\x00\x00\x00\x57\x41\x56\x45\x66\x6d\x74\x20\x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00\x64\x61\x74\x61\x00\x00\x00\x00'
            
            # Generate speech using OpenAI TTS
            if self.client is None:
                raise Exception("OpenAI client not initialized")
                
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=self.tts_voice,
                input=text
            )
            audio_data = response.content
            print(f"[SpeechService] TTS audio generated. Bytes length: {len(audio_data)}")
            
            return audio_data
            
        except Exception as e:
            print(f"[SpeechService] ERROR in text_to_speech: {e}")
            raise Exception(f"Text-to-speech conversion failed: {str(e)}")
    
    def process_audio_chunk(self, audio_chunk: bytes, sample_rate: int = 16000) -> bytes:
        print(f"[SpeechService] process_audio_chunk called. Bytes length: {len(audio_chunk)}")
        """
        Process audio chunk for optimal STT performance
        
        Args:
            audio_chunk: Raw audio chunk
            sample_rate: Audio sample rate
            
        Returns:
            Processed audio data
        """
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_chunk, dtype=np.int16)
            
            # Normalize audio
            audio_array = audio_array.astype(np.float32) / 32768.0
            
            # Convert back to bytes
            processed_audio = (audio_array * 32768).astype(np.int16).tobytes()
            print(f"[SpeechService] Audio chunk processed. Output bytes length: {len(processed_audio)}")
            
            return processed_audio
            
        except Exception as e:
            print(f"[SpeechService] ERROR in process_audio_chunk: {e}")
            raise Exception(f"Audio processing failed: {str(e)}")
    
    def base64_to_audio(self, base64_audio: str) -> bytes:
        print(f"[SpeechService] base64_to_audio called. Input length: {len(base64_audio)}")
        """
        Convert base64 encoded audio to bytes
        
        Args:
            base64_audio: Base64 encoded audio string
            
        Returns:
            Audio data in bytes
        """
        try:
            # Remove data URL prefix if present
            if base64_audio.startswith('data:audio/'):
                base64_audio = base64_audio.split(',')[1]
            
            # Decode base64
            audio_data = base64.b64decode(base64_audio)
            print(f"[SpeechService] base64 decoded. Output bytes length: {len(audio_data)}")
            return audio_data
            
        except Exception as e:
            print(f"[SpeechService] ERROR in base64_to_audio: {e}")
            raise Exception(f"Base64 audio conversion failed: {str(e)}")
    
    def audio_to_base64(self, audio_data: bytes) -> str:
        print(f"[SpeechService] audio_to_base64 called. Input bytes length: {len(audio_data)}")
        """
        Convert audio bytes to base64 string
        
        Args:
            audio_data: Audio data in bytes
            
        Returns:
            Base64 encoded audio string
        """
        try:
            base64_audio = base64.b64encode(audio_data).decode('utf-8')
            print(f"[SpeechService] audio_to_base64 output length: {len(base64_audio)}")
            return base64_audio
            
        except Exception as e:
            print(f"[SpeechService] ERROR in audio_to_base64: {e}")
            raise Exception(f"Audio to base64 conversion failed: {str(e)}")
    
    def validate_audio_format(self, audio_data: bytes) -> bool:
        print(f"[SpeechService] validate_audio_format called. Bytes length: {len(audio_data)}")
        """
        Validate audio format for processing. Accepts WebM, Opus, MP3, WAV, etc.
        
        Args:
            audio_data: Audio data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Try to load with pydub (which uses ffmpeg)
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
            print("[SpeechService] Audio format valid (pydub).")
            return True
        except Exception as e:
            print(f"[SpeechService] Audio format invalid: {e}")
            return False


# Create global speech service instance
speech_service = SpeechService() 