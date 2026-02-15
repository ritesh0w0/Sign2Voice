from deep_translator import GoogleTranslator

# Language Code Mapping
LANG_CODE_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn"
}

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
        "Telugu": "నమస్కారం"
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
    }
}

def translate_text(text: str, target_language: str) -> str:
    """
    Translates text to the target language using Dictionary Lookup (Primary) or Google Translate (Fallback).
    """
    if target_language == "English":
        return text 
    
    # 1. Check Demo Dictionary (Fast & Accurate)
    if text in DEMO_TRANSLATIONS:
        if target_language in DEMO_TRANSLATIONS[text]:
            return DEMO_TRANSLATIONS[text][target_language]
    
    # 2. Fallback to Deep Translator
    target_code = LANG_CODE_MAP.get(target_language, "en")
    
    try:
        translator = GoogleTranslator(source='auto', target=target_code)
        translation = translator.translate(text)
        return translation
    except Exception as e:
        print(f"Translation Error: {e}")
        return text # Fallback to original
