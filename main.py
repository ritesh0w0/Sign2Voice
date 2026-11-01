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
    "Hello, whats up": {
        "Kannada": "ನಮಸ್ಕಾರ, ಏನ ಸಮಾಚಾರ?",
        "Hindi": "नमस्ते, क्या हाल है?",
        "Tamil": "வணக்கம், என்ன விஷயம்?",
        "Telugu": "హలో, ఎలా ఉన్నారు?"
    },
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
    "I truly appreciate you.": {
        "Kannada": "ನಾನು ನಿಮ್ಮನ್ನು ನಿಜವಾಗಿಯೂ ಮೆಚ್ಚುತ್ತೇನೆ.",
        "Hindi": "मैं वास्तव में आपकी प्रशंसा करता हूं.",
        "Tamil": "நான் உங்களை உண்மையிலேயே பாராட்டுகிறேன்.",
        "Telugu": "నేను నిన్ను నిజంగా అభినందిస్తున్నాను."
    },
    "Yes! We are the champions.": {
        "Kannada": "ಹೌದು! ನಾವು ಚಾಂಪಿಯನ್ಸ್.",
        "Hindi": "हाँ! हम विजेता हैं.",
        "Tamil": "ஆம்! நாம் சாம்பியன்கள்.",
        "Telugu": "అవును! మనం విజేతలం."
    },
    "I am in trouble, please help me immediately.": {
        "Kannada": "ನಾನು ಕಷ್ಟದಲ್ಲಿದ್ದೇನೆ, ದಯವಿಟ್ಟು ತಕ್ಷಣ ಸಹಾಯ ಮಾಡಿ.",
        "Hindi": "मैं मुसीबत में हूँ, कृपया तुरंत मेरी मदद करें.",
        "Tamil": "நான் சிக்கலில் உள்ளேன், தயவுசெய்து உடனடியாக உதவுங்கள்.",
        "Telugu": "నేను సమస్యలో ఉన్నాను, దయచేసి వెంటనే సహాయం చేయండి."
    },
    "Yes, I need some assistance please.": {
        "Kannada": "ಹೌದು, ನನಗೆ ದಯವಿಟ್ಟು ಸ್ವಲ್ಪ ಸಹಾಯ ಬೇಕು.",
        "Hindi": "हाँ, मुझे कृपया कुछ सहायता चाहिए.",
        "Tamil": "ஆம், எனக்கு தயவுசெய்து உதவி தேவை.",
        "Telugu": "అవును, నాకు దయచేసి కాస్త సహాయం కావాలి."
    },
    "Please help me!": {
        "Kannada": "ದಯವಿಟ್ಟು ನನಗೆ ಸಹಾಯ ಮಾಡಿ!",
        "Hindi": "कृपया मेरी मदद करें!",
        "Tamil": "தயவுசெய்து எனக்கு உதவுங்கள்!",
        "Telugu": "దయచేసి నాకు సహాయం చేయండి!"
    }
}

# Pre-warm common TTS audio clips on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 55)
    print("  Sign2Voice Server Starting - Pre-warming Audio Cache...")
    print("=" * 55)
    langs = ["Kannada", "Hindi", "Telugu", "Tamil", "English"]
    for lang in langs:
        txt = SENTENCE_TRANSLATIONS.get("Hello, whats up", {}).get(lang, "")
        if not txt and lang == "English":
            txt = "Hello, whats up"
        if txt:
            try:
                await generate_audio(txt, lang)
            except Exception as e:
                pass
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
    """Returns available target languages and complete gesture vocabulary."""
    return {
        "languages": list(LANG_CODE_MAP.keys()),
        "signs": [
            {"sign": "Hello", "description": "Open hand with slight waving motion", "icon": "👋"},
            {"sign": "Yes", "description": "Fist with thumb pointed upwards", "icon": "👍"},
            {"sign": "No", "description": "Fist with thumb pointed downwards", "icon": "👎"},
            {"sign": "2", "description": "Index and middle fingers extended (Victory / Peace)", "icon": "✌️"},
            {"sign": "I Love You", "description": "Thumb, index finger, and pinky extended (ASL ILY)", "icon": "🤟"},
            {"sign": "Help", "description": "Thumb and pinky extended (Emergency / Call me)", "icon": "🤙"},
            {"sign": "OK", "description": "Thumb and index tips touching in circle, 3 fingers open", "icon": "👌"},
            {"sign": "Rock", "description": "Index and pinky open, middle and ring folded (Horns)", "icon": "🤘"},
            {"sign": "Fist", "description": "All fingers closed into a fist (Stop / Strength)", "icon": "✊"},
            {"sign": "1", "description": "Index finger extended upwards", "icon": "☝️"},
            {"sign": "3", "description": "Index, middle, and ring fingers extended", "icon": "🤟"},
            {"sign": "4", "description": "Four fingers open with thumb tucked into palm", "icon": "🖖"},
            {"sign": "5", "description": "All five fingers open, static hand", "icon": "✋"},
            {"sign": "L", "description": "Thumb and index finger forming 90° L shape", "icon": "🇱"},
            {"sign": "Y", "description": "Thumb and pinky finger open (ASL Y)", "icon": "🇾"}
        ]
    }


@app.post("/process_frame")
async def process_frame(
    image: UploadFile = File(...),
    target_language: str = Form("English")
):
    """
    Core frame recognition:
    Detects current gesture and returns predicted sign and landmark telemetry.
    (Individual word audio is omitted so only the full sentence is spoken).
    """
    image_bytes = await image.read()

    # 1. Sign Recognition
    sign_text, debug_info = recognizer.detect_sign(image_bytes)

    # 2. Translation for UI preview
    is_valid_sign = (
        bool(sign_text)
        and sign_text not in ["No Hand Detected", "Unknown Sign"]
        and not sign_text.startswith("Error")
    )

    if not is_valid_sign:
        translated_text = "..."
    else:
        translated_text = translate_text(sign_text, target_language)

    return {
        "sign_text": sign_text,
        "translated_text": translated_text,
        "audio_url": "",
        "debug_info": debug_info
    }


@app.post("/process_sentence")
async def process_sentence(request: SentenceRequest):
    """
    Automatic Sentence Synthesizer:
    Synthesizes accumulated tokens into natural speech and generates Edge-TTS audio.
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

    # 3. Neural TTS synthesis for the final sentence
    audio_url = await generate_audio(translated_text, request.target_language)

    return {
        "original": natural_text,
        "translated": translated_text,
        "audio_url": audio_url
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
