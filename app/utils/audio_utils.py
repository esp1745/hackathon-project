"""
Audio utility functions for processing and validation
"""

import numpy as np
import io
import wave
from typing import Tuple, Optional
import soundfile as sf


def validate_audio_format(audio_data: bytes) -> bool:
    """
    Validate if audio data is in a supported format
    
    Args:
        audio_data: Raw audio data
        
    Returns:
        True if valid, False otherwise
    """
    try:
        with io.BytesIO(audio_data) as audio_io:
            sf.read(audio_io)
        return True
    except Exception:
        return False


def convert_audio_format(
    audio_data: bytes, 
    target_format: str = "wav",
    sample_rate: int = 16000,
    channels: int = 1
) -> bytes:
    """
    Convert audio to target format
    
    Args:
        audio_data: Input audio data
        target_format: Target format (wav, mp3, etc.)
        sample_rate: Target sample rate
        channels: Number of channels
        
    Returns:
        Converted audio data
    """
    try:
        # Read audio data
        with io.BytesIO(audio_data) as audio_io:
            data, original_sample_rate = sf.read(audio_io)
        
        # Resample if needed
        if original_sample_rate != sample_rate:
            # Simple resampling (in production, use proper resampling)
            ratio = sample_rate / original_sample_rate
            new_length = int(len(data) * ratio)
            data = np.interp(
                np.linspace(0, len(data), new_length),
                np.arange(len(data)),
                data
            )
        
        # Convert to mono if needed
        if len(data.shape) > 1 and data.shape[1] > channels:
            data = np.mean(data, axis=1)
        
        # Write to target format
        output_io = io.BytesIO()
        sf.write(output_io, data, sample_rate, format=target_format.upper())
        return output_io.getvalue()
        
    except Exception as e:
        raise Exception(f"Audio conversion failed: {str(e)}")


def normalize_audio(audio_data: bytes) -> bytes:
    """
    Normalize audio levels
    
    Args:
        audio_data: Input audio data
        
    Returns:
        Normalized audio data
    """
    try:
        # Read audio data
        with io.BytesIO(audio_data) as audio_io:
            data, sample_rate = sf.read(audio_io)
        
        # Normalize
        if np.max(np.abs(data)) > 0:
            data = data / np.max(np.abs(data)) * 0.95
        
        # Write back
        output_io = io.BytesIO()
        sf.write(output_io, data, sample_rate)
        return output_io.getvalue()
        
    except Exception as e:
        raise Exception(f"Audio normalization failed: {str(e)}")


def get_audio_info(audio_data: bytes) -> dict:
    """
    Get audio file information
    
    Args:
        audio_data: Audio data
        
    Returns:
        Audio information dictionary
    """
    try:
        with io.BytesIO(audio_data) as audio_io:
            data, sample_rate = sf.read(audio_io)
        
        return {
            "sample_rate": sample_rate,
            "channels": len(data.shape),
            "duration": len(data) / sample_rate,
            "format": "audio",
            "shape": data.shape
        }
    except Exception as e:
        raise Exception(f"Failed to get audio info: {str(e)}")


def create_silence(duration: float, sample_rate: int = 16000) -> bytes:
    """
    Create silence audio
    
    Args:
        duration: Duration in seconds
        sample_rate: Sample rate
        
    Returns:
        Silence audio data
    """
    try:
        samples = int(duration * sample_rate)
        silence = np.zeros(samples)
        
        output_io = io.BytesIO()
        sf.write(output_io, silence, sample_rate)
        return output_io.getvalue()
        
    except Exception as e:
        raise Exception(f"Failed to create silence: {str(e)}")


def chunk_audio(audio_data: bytes, chunk_duration: float = 1.0) -> list:
    """
    Split audio into chunks
    
    Args:
        audio_data: Audio data
        chunk_duration: Duration of each chunk in seconds
        
    Returns:
        List of audio chunks
    """
    try:
        with io.BytesIO(audio_data) as audio_io:
            data, sample_rate = sf.read(audio_io)
        
        chunk_samples = int(chunk_duration * sample_rate)
        chunks = []
        
        for i in range(0, len(data), chunk_samples):
            chunk_data = data[i:i + chunk_samples]
            
            # Pad last chunk if needed
            if len(chunk_data) < chunk_samples:
                chunk_data = np.pad(chunk_data, (0, chunk_samples - len(chunk_data)))
            
            # Convert chunk to bytes
            chunk_io = io.BytesIO()
            sf.write(chunk_io, chunk_data, sample_rate)
            chunks.append(chunk_io.getvalue())
        
        return chunks
        
    except Exception as e:
        raise Exception(f"Failed to chunk audio: {str(e)}") 