import asyncio
import os
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from sign_recognition import SignRecognizer
from translation_service import translate_text, DEMO_TRANSLATIONS, LANG_CODE_MAP
from tts_service import generate_audio
from sentence_engine import sentence_engine

# Ensure static directories exist before mounting
os.makedirs("static", exist_ok=True)
os.makedirs(os.path.join("static", "audio"), exist_ok=True)

# Curated Natural Demo Overrides for multi-lingual fluency
SENTENCE_TRANSLATIONS = {
    "Hello! Everything looks good.": {
        "Kannada": "ನಮಸ್ಕಾರ! ಎಲ್ಲವೂ ಸರಿಯಾಗಿದೆ.",
        "Hindi": "नमस्ते! सब कुछ ठीक है.",
        "Tamil": "வணக்கம்! எல்லாம் சரியாக உள்ளது.",
        "Telugu": "నమస్కారం! అంతా బాగుంది."
    },
    "Hello! It is wonderful to see you.": {
        "Kannada": "ನಮಸ್ಕಾರ! ನಿಮ್ಮನ್ನು ನೋಡಿ ತುಂಬಾ ಸಂತೋಷವಾಯಿತು.",
        "Hindi": "नमस्ते! आपसे मिलकर बहुत खुशी हुई.",
        "Tamil": "வணக்கம்! உங்களை பார்ப்பதில் மிக்க மகிழ்ச்சி.",
        "Telugu": "నమస్కారం! మిమ్మల్ని చూడటం చాలా ఆనందంగా ఉంది."
    },
    "Greetings! We have achieved success.": {
        "Kannada": "ನಮಸ್ಕಾರ! ನಾವು ಯಶಸ್ಸನ್ನು ಸಾಧಿಸಿದ್ದೇವೆ.",
        "Hindi": "नमस्ते! हमने सफलता प्राप्त की है.",
        "Tamil": "வணக்கம்! நாம் வெற்றியை அடைந்துள்ளோம்.",
        "Telugu": "నమస్కారం! మనం విజయం సాధించాం."
    },
    "I truly appreciate and love you.": {
        "Kannada": "ನಾನು ನಿಮ್ಮನ್ನು ನಿಜವಾಗಿಯೂ ಪ್ರೀತಿಸುತ್ತೇನೆ ಮತ್ತು ಗೌರವಿಸುತ್ತೇನೆ.",
        "Hindi": "मैं वास्तव में आपकी सराहना और आपसे प्यार करता हूँ.",
        "Tamil": "நான் உங்களை உண்மையிலேயே நேசிக்கிறேன்.",
        "Telugu": "నేను నిన్ను నిజంగా ప్రేమిస్తున్నాను."
    },
    "Hello! How can I assist you?": {
        "Kannada": "ನಮಸ್ಕಾರ, ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
        "Hindi": "नमस्ते, मैं आपकी क्या मदद कर सकता हूँ?",
        "Tamil": "வணக்கம், நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
        "Telugu": "నమస్కారం, నేను మీకు ఎలా సహాయం చేయగలను?"
    },
    "I need help right away, please assist me.": {
        "Kannada": "ನನಗೆ ತಕ್ಷಣ ಸಹಾಯ ಬೇಕಾಗಿದೆ, ದಯವಿಟ್ಟು ಸಹಾಯ ಮಾಡಿ.",
        "Hindi": "मुझे तुरंत मदद की ज़रूरत है, कृपया सहायता करें.",
        "Tamil": "எனக்கு உடனடியாக உதவி தேவை, தயவுசெய்து உதவுங்கள்.",
        "Telugu": "నాకు వెంటనే సహాయం కావాలి, దయచేసి సహాయం చేయండి."
    }
}

# Pre-warm common TTS audio clips on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 55)
    print("  Sign2Voice Server Starting - Pre-warming Audio Cache...")
    print("=" * 55)
    prewarm_samples = [
        ("Hello! How can I assist you?", "English"),
        ("नमस्ते! सब कुछ ठीक है.", "Hindi"),
        ("ನಮಸ್ಕಾರ! ಎಲ್ಲವೂ ಸರಿಯಾಗಿದೆ.", "Kannada")
    ]
    for text, lang in prewarm_samples:
        try:
            await generate_audio(text, lang)
        except Exception as e:
            print(f"[Warmup Ignored] {e}")
    print("[Sign2Voice] Cache Warmup Complete. Service is ready!")
    yield
    print("[Sign2Voice] Server shutting down cleanly.")


app = FastAPI(
    title="Sign2Voice API",
    description="Real-time Sign Language Gesture Recognition, Multilingual Translation & Voice Synthesis",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Vision Engine
recognizer = SignRecognizer()


class SentenceRequest(BaseModel):
    tokens: List[str]
    target_language: str = "English"


@app.get("/")
async def read_root():
    """Serves the main Glassmorphic Web Dashboard."""
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        {"message": "Sign2Voice API is live. static/index.html is being prepared."},
        status_code=200
    )


@app.get("/api/health")
async def health_check():
    """System health check and diagnostic status."""
    return {
        "status": "healthy",
        "service": "Sign2Voice",
        "vision_engine": "MediaPipe Hands",
        "tts_engine": "Edge-TTS Neural",
        "version": "2.0.0"
    }


@app.get("/api/supported")
async def get_supported_info():
    """Returns available target languages and gesture vocabulary."""
    return {
        "languages": list(LANG_CODE_MAP.keys()),
        "signs": [
            {"sign": "Hello", "description": "Open hand with slight waving motion", "icon": "👋"},
            {"sign": "Yes", "description": "Fist with thumb pointed upwards", "icon": "👍"},
            {"sign": "No", "description": "Fist with thumb pointed downwards", "icon": "👎"},
            {"sign": "Victory", "description": "V-sign with index and middle fingers", "icon": "✌️"},
            {"sign": "I Love You", "description": "Thumb, index finger, and pinky extended (ASL ILY)", "icon": "🤟"},
            {"sign": "Help", "description": "Fist with thumb and pinky extended (Emergency)", "icon": "🤙"},
            {"sign": "1", "description": "Index finger extended upwards", "icon": "☝️"},
            {"sign": "2", "description": "Index and middle fingers extended", "icon": "✌️"},
            {"sign": "3", "description": "Index, middle, and ring fingers extended", "icon": "🤟"},
            {"sign": "4", "description": "Four fingers open with thumb tucked", "icon": "🖖"},
            {"sign": "5", "description": "All five fingers open, static hand", "icon": "✋"},
            {"sign": "L", "description": "Thumb and index finger forming L shape", "icon": "🇱"},
            {"sign": "Y", "description": "Thumb and pinky finger open (ASL Y)", "icon": "🇾"}
        ]
    }


@app.post("/process_frame")
async def process_frame(
    image: UploadFile = File(...),
    target_language: str = Form("English")
):
    """
    Core computer vision pipeline:
    1. MediaPipe Hand Landmark Detection
    2. Geometric Gesture Recognition
    3. Multilingual Translation
    4. Neural Text-To-Speech Synthesis
    """
    image_bytes = await image.read()

    # 1. Sign Recognition
    sign_text, debug_info = recognizer.detect_sign(image_bytes)

    # 2. Translation & TTS Validation
    is_valid_sign = (
        bool(sign_text)
        and sign_text not in ["No Hand Detected", "Unknown Sign"]
        and not sign_text.startswith("Error")
    )

    if not is_valid_sign:
        translated_text = "..."
        audio_url = ""
    else:
        # Multilingual Translation
        translated_text = translate_text(sign_text, target_language)

        # Neural TTS Synthesis
        try:
            audio_url = await generate_audio(translated_text, target_language)
        except Exception as e:
            print(f"[TTS Pipeline Warning] {e}")
            audio_url = ""

    return {
        "sign_text": sign_text,
        "translated_text": translated_text,
        "audio_url": audio_url,
        "debug_info": debug_info
    }


@app.post("/process_sentence")
async def process_sentence(request: SentenceRequest):
    """
    Sentence builder pipeline:
    Synthesizes a list of accumulated tokens into fluent speech.
    """
    natural_text = sentence_engine.construct_sentence(request.tokens)

    if not natural_text:
        return {"original": "", "translated": "", "audio_url": ""}

    # 1. Check curated natural translations first
    translated_text = ""
    if natural_text in SENTENCE_TRANSLATIONS:
        if request.target_language in SENTENCE_TRANSLATIONS[natural_text]:
            translated_text = SENTENCE_TRANSLATIONS[natural_text][request.target_language]

    # 2. Dynamic translator fallback
    if not translated_text:
        translated_text = translate_text(natural_text, request.target_language)

    # 3. Neural TTS synthesis
    audio_url = await generate_audio(translated_text, request.target_language)

    return {
        "original": natural_text,
        "translated": translated_text,
        "audio_url": audio_url
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
