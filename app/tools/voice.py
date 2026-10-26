"""Voice input using Groq Whisper."""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """Transcribe audio using Groq's Whisper model."""
    if not audio_bytes or len(audio_bytes) > 24 * 1024 * 1024:
        return "Voice Error: Record a shorter message (under 24 MB)."
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY not found."
        
    client = Groq(api_key=api_key, timeout=45, max_retries=1)
    
    try:
        transcription = client.audio.transcriptions.create(
            file=(filename, audio_bytes),
            model="whisper-large-v3",
            response_format="text",
            temperature=0.0
            # We removed the language parameter so it auto-detects Malayalam
        )
        
        # Handle different return types from Groq
        if hasattr(transcription, 'text'):
            return transcription.text
        elif isinstance(transcription, dict):
            return transcription.get('text', str(transcription))
        else:
            return str(transcription).strip()
            
    except Exception as e:
        return "Voice Error: Transcription failed. Please retry or type your message."