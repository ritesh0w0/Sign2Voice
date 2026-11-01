import edge_tts
import os
import uuid
import glob

# Audio directory setup
AUDIO_DIR = os.path.join("static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Voice Mapping for natural neural speech
VOICE_MAP = {
    "English": "en-US-AriaNeural",
    "Hindi": "hi-IN-SwaraNeural",
    "Tamil": "ta-IN-PallaviNeural",
    "Telugu": "te-IN-ShrutiNeural",
    "Kannada": "kn-IN-GaganNeural"
}

# Audio Cache: {(text, language): filename}
AUDIO_CACHE = {}
MAX_CACHED_FILES = 150

def _prune_audio_cache():
    """Keeps the audio directory clean by removing old files if count exceeds threshold."""
    try:
        files = glob.glob(os.path.join(AUDIO_DIR, "*.mp3"))
        if len(files) > MAX_CACHED_FILES:
            # Sort by modification time
            files.sort(key=os.path.getmtime)
            # Remove oldest 30 files
            for f in files[:30]:
                try:
                    os.remove(f)
                except OSError:
                    pass
    except Exception as e:
        print(f"[Cache Pruning Warning] {e}")

async def generate_audio(text: str, language: str) -> str:
    """
    Generates neural audio with caching.
    Returns the relative URL path to the generated MP3.
    """
    if not text or not isinstance(text, str) or text.strip() in ["", "..."]:
        return ""
    
    clean_text = text.strip()
    cache_key = (clean_text, language)

    # Check cache
    if cache_key in AUDIO_CACHE:
        cache_filename = AUDIO_CACHE[cache_key]
        cache_file = os.path.join(AUDIO_DIR, cache_filename)
        if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
            return f"/static/audio/{cache_filename}"

    voice = VOICE_MAP.get(language, "en-US-AriaNeural")
    filename = f"{uuid.uuid4().hex[:12]}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    try:
        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save(filepath)

        # Validation
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            print(f"[TTS Error] Zero-byte audio produced for: '{clean_text}'")
            return ""

        AUDIO_CACHE[cache_key] = filename
        _prune_audio_cache()
        return f"/static/audio/{filename}"

    except Exception as e:
        print(f"[TTS Generation Failed] '{clean_text}' ({language}): {e}")
        return ""
