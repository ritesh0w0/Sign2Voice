from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
from sign_recognition import SignRecognizer
from translation_service import translate_text
from tts_service import generate_audio
import uuid

app = FastAPI()

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Recognizer
recognizer = SignRecognizer()

class PipelineResponse(BaseModel):
    sign_text: str
    translated_text: str
    audio_url: str

@app.get("/")
async def read_root():
    # Return index.html
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

@app.post("/process_frame")
async def process_frame(
    image: UploadFile = File(...),
    target_language: str = Form(...)
):
    # Read image bytes
    image_bytes = await image.read()
    
    # 1. Sign Recognition
    sign_text, debug_info = recognizer.detect_sign(image_bytes)
    
    # 2. Translation
    # Only translate if valid sign
    # Added robust check for Error states from Recognizer
    is_valid_sign = (
        sign_text 
        and sign_text not in ["No Hand Detected", "Unknown Sign"] 
        and not sign_text.startswith("Error")
    )

    if not is_valid_sign:
        translated_text = "..."
        if sign_text.startswith("Error"):
             # Optional: Return the error as text to debug? 
             # For UI cleanliness, we might just keep "..." or show a specific error
             pass
        audio_url = ""
    else:
        translated_text = translate_text(sign_text, target_language)
        
        # 3. TTS
        try:
            audio_url = await generate_audio(translated_text, target_language)
        except Exception as e:
            print(f"TTS Generation Failed: {e}")
            audio_url = "" # Fail gracefully without crashing response
    
    return {
        "sign_text": sign_text,
        "translated_text": translated_text,
        "audio_url": audio_url,
        "debug_info": debug_info
    }

from sentence_engine import sentence_engine

class SentenceRequest(BaseModel):
    tokens: list[str]
    target_language: str

# Hardcoded overrides for perfect demo speech
SENTENCE_TRANSLATIONS = {
    "Hello! Everything looks good.": {
        "Kannada": "ನಮಸ್ಕಾರ! ಎಲ್ಲವೂ ಸರಿಯಾಗಿದೆ.",
        "Hindi": "नमस्ते! सब कुछ ठीक है.",
        "Tamil": "வணக்கம்! எல்லாம் சரியாக உள்ளது.",
        "Telugu": "నమస్కారం! అంతా బాగుంది."
    },
    "Hello! It is wonderful to see you.": { 
         # Used to be "Hello" + "I Love You"
         "Kannada": "ನಮಸ್ಕಾರ! ನಿಮ್ಮನ್ನು ನೋಡಿ ತುಂಬಾ ಸಂತೋಷವಾಯಿತು.",
         "Hindi": "नमस्ते! आपसे मिलकर बहुत खुशी हुई.",
         "Telugu": "నమస్కారం! మిమ్మల్ని చూడటం చాలా ఆనందంగా ఉంది."
    },
    "Greetings! We have achieved success.": {
         # Hello + 2
         "Kannada": "ನಮಸ್ಕಾರ! ನಾವು ಯಶಸ್ಸನ್ನು ಸಾಧಿಸಿದ್ದೇವೆ.",
         "Hindi": "नमस्ते! हमने सफलता प्राप्त की है.",
         "Telugu": "నమస్కారం! మనం విజయం సాధించాం."
    },
    "I truly appreciate you.": {
         "Kannada": "ನಾನು ನಿಮ್ಮನ್ನು ನಿಜವಾಗಿಯೂ ಮೆಚ್ಚುತ್ತೇನೆ.",
         "Hindi": "मैं वास्तव में आपकी प्रशंसा करता हूं.",
         "Telugu": "నేను నిన్ను నిజంగా అభినందిస్తున్నాను."
    },
    "Hello, whats up": {
         "Kannada": "ನಮಸ್ಕಾರ, ಏನ ಸಮಾಚಾರ?",
         "Hindi": "नमस्ते, क्या हाल है?",
         "Telugu": "హలో, ఎలా ఉన్నారు?"
    }
}

@app.post("/process_sentence")
async def process_sentence(request: SentenceRequest):
    # 1. Construct Natural Sentence
    natural_text = sentence_engine.construct_sentence(request.tokens)
    
    # 2. Translate
    if not natural_text:
        return {"original": "", "translated": "", "audio_url": ""}
        
    # Check Hardcoded Sentence Map first
    translated_text = ""
    if natural_text in SENTENCE_TRANSLATIONS:
         if request.target_language in SENTENCE_TRANSLATIONS[natural_text]:
             translated_text = SENTENCE_TRANSLATIONS[natural_text][request.target_language]
    
    # Fallback to Deep Translator
    if not translated_text:
        translated_text = translate_text(natural_text, request.target_language)
    
    # 3. TTS
    audio_url = await generate_audio(translated_text, request.target_language)
    
    return {
        "original": natural_text,
        "translated": translated_text,
        "audio_url": audio_url
    }

    return {
        "original": natural_text,
        "translated": translated_text,
        "audio_url": audio_url
    }

# --- PERFORMANCE OPTIMIZATION ---
# Pre-warm Audio Cache
import asyncio

@app.on_event("startup")
async def prewarm_cache():
    print("Pre-warming Audio Cache...")
    # List of common languages to cache
    langs = ["Kannada", "Hindi", "Telugu", "English"]
    
    # Cache "Hello, whats up" in all langs
    for lang in langs:
         # Check maps
         txt = SENTENCE_TRANSLATIONS.get("Hello, whats up", {}).get(lang, "")
         if not txt and lang == "English": txt = "Hello, whats up"
         
         if txt:
             try:
                 await generate_audio(txt, lang)
             except: pass
             
    print("Cache Warmup Complete.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
