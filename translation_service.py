from typing import Optional
from deep_translator import GoogleTranslator

# Language Code Mapping
LANG_CODE_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn"
}

# Fast offline dictionary for instant demo translation
DEMO_TRANSLATIONS = {
    "No": {
        "Kannada": "ಇಲ್ಲ", 
        "Hindi": "नहीं",
        "Tamil": "இல்லை",
        "Telugu": "కాదు"
    },
    "Yes": {
        "Kannada": "ಹೌದು",
        "Hindi": "हाँ",
        "Tamil": "ஆம்",
        "Telugu": "అవును"
    },
    "Hello": {
        "Kannada": "ನಮಸ್ಕಾರ",
        "Hindi": "नमस्ते",
        "Tamil": "வணக்கம்",
        "Telugu": "నಮస్కారం"
    },
    "I Love You": {
        "Kannada": "ನಾನು ನಿನ್ನನ್ನು ಪ್ರೀತಿಸುತ್ತೇನೆ",
        "Hindi": "मैं तुमसे प्यार करता हूँ",
        "Tamil": "நான் உன்னை காதலிக்கிறேன்",
        "Telugu": "నేను నిన్ను ప్రేమిస్తున్నాను"
    },
    "Help": {
        "Kannada": "ಸಹಾಯ",
        "Hindi": "मदद",
        "Tamil": "உதவி",
        "Telugu": "సహాయం"
    },
    "Victory": {
        "Kannada": "ಜಯ",
        "Hindi": "जीत",
        "Tamil": "வெற்றி",
        "Telugu": "విజయం"
    },
    "2": {
        "Kannada": "ಎರಡು",
        "Hindi": "दो",
        "Tamil": "இரண்டு",
        "Telugu": "రెండు"
    },
    "1": {
        "Kannada": "ಒಂದು",
        "Hindi": "एक",
        "Tamil": "ஒன்று",
        "Telugu": "ఒకటి"
    },
    "3": {
        "Kannada": "ಮೂರು",
        "Hindi": "तीन",
        "Tamil": "மூன்று",
        "Telugu": "మూడు"
    },
    "4": {
        "Kannada": "ನಾಲ್ಕು",
        "Hindi": "चार",
        "Tamil": "நான்கு",
        "Telugu": "నాలుగు"
    },
    "5": {
        "Kannada": "ಐದು",
        "Hindi": "पाँच",
        "Tamil": "ஐந்து",
        "Telugu": "ఐదు"
    },
    "OK": {
        "Kannada": "ಸರಿ",
        "Hindi": "ठीक है",
        "Tamil": "சரி",
        "Telugu": "సరే"
    },
    "Rock": {
        "Kannada": "ಅದ್ಭುತ (Rock)",
        "Hindi": "शानदार",
        "Tamil": "அற்புதம்",
        "Telugu": "అద్భుతం"
    },
    "Fist": {
        "Kannada": "ಮುಷ್ಟಿ (Stop)",
        "Hindi": "मुट्ठी",
        "Tamil": "கைப்பிடி",
        "Telugu": "పిడికిలి"
    },
    "L": {
        "Kannada": "ಅಕ್ಷರ L",
        "Hindi": "अक्षर L",
        "Tamil": "எழுத்து L",
        "Telugu": "అక్షరం L"
    },
    "Y": {
        "Kannada": "ಅಕ್ಷರ Y",
        "Hindi": "अक्षर Y",
        "Tamil": "எழுத்து Y",
        "Telugu": "அಕ್ಷరం Y"
    }
}

def translate_text(text: str, target_language: str) -> str:
    """
    Translates text to the target language using Dictionary Lookup (Primary) or Google Translate (Fallback).
    """
    if not text or target_language == "English":
        return text 
    
    # 1. Check Demo Dictionary (Ultra-fast & offline accurate)
    if text in DEMO_TRANSLATIONS:
        if target_language in DEMO_TRANSLATIONS[text]:
            return DEMO_TRANSLATIONS[text][target_language]
    
    # 2. Fallback to Deep Translator
    target_code = LANG_CODE_MAP.get(target_language, "en")
    
    try:
        translator = GoogleTranslator(source='auto', target=target_code)
        translation = translator.translate(text)
        return translation if translation else text
    except Exception as e:
        print(f"[Translation Warning] Fallback triggered: {e}")
        return text
