import edge_tts
import os
import uuid

# Create audio directory
AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Voice Mapping
VOICE_MAP = {
    "English": "en-US-AriaNeural",
    "Hindi": "hi-IN-SwaraNeural",
    "Tamil": "ta-IN-PallaviNeural",
    "Telugu": "te-IN-ShrutiNeural",
    "Kannada": "kn-IN-GaganNeural"
}

# Audio Cache: {(text, language): filename}
AUDIO_CACHE = {}

async def generate_audio(text: str, language: str) -> str:
    """
    Generates audio with caching.
    """
    if (text, language) in AUDIO_CACHE:
        # Verify file still exists
        cache_file = os.path.join(AUDIO_DIR, AUDIO_CACHE[(text, language)])
        if os.path.exists(cache_file):
            print(f"TTS Cache Hit: {text}")
            return f"/static/audio/{AUDIO_CACHE[(text, language)]}"
    
    voice = VOICE_MAP.get(language, "en-US-AriaNeural")
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    
    if not text or not isinstance(text, str):
        print(f"TTS Error: Invalid text input: {text}")
        return ""

    communicate = edge_tts.Communicate(str(text), voice)
    await communicate.save(filepath)
    
    # Validation
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print(f"TTS Error: File generation failed for {text}")
        return ""
        
    print(f"TTS Success: Generated {filename} ({os.path.getsize(filepath)} bytes)")
    return f"/static/audio/{filename}"
