# Sign2Voice REST API Documentation

Sign2Voice exposes an asynchronous REST API built with FastAPI for real-time sign language gesture detection, sequence token accumulation, multilingual text translation, and neural text-to-speech synthesis.

Base URL: `http://localhost:8000`  
Interactive Swagger Docs: `http://localhost:8000/docs`  
ReDoc Documentation: `http://localhost:8000/redoc`

---

## Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the Glassmorphic Web Dashboard interface |
| `GET` | `/api/health` | Service health status and engine versions |
| `GET` | `/api/supported` | Returns supported target languages and gesture vocabulary |
| `POST` | `/process_frame` | Processes a webcam frame: detects gesture, translates text, and returns TTS audio |
| `POST` | `/process_sentence` | Synthesizes a list of accumulated tokens into natural speech |

---

## 1. System Health Check

### `GET /api/health`

Returns operational telemetry and engine readiness status.

#### Response `200 OK`
```json
{
  "status": "healthy",
  "service": "Sign2Voice",
  "vision_engine": "MediaPipe Hands",
  "tts_engine": "Edge-TTS Neural",
  "version": "2.0.0"
}
```

---

## 2. Supported Languages & Signs

### `GET /api/supported`

Returns all active language locales and recognized gesture signs with descriptions.

#### Response `200 OK`
```json
{
  "languages": [
    "English",
    "Hindi",
    "Tamil",
    "Telugu",
    "Kannada"
  ],
  "signs": [
    {
      "sign": "Hello",
      "description": "Open hand with slight waving motion",
      "icon": "👋"
    },
    {
      "sign": "Yes",
      "description": "Fist with thumb pointed upwards",
      "icon": "👍"
    },
    {
      "sign": "Victory",
      "description": "V-sign with index and middle fingers",
      "icon": "✌️"
    }
  ]
}
```

---

## 3. Process Video Frame

### `POST /process_frame`

Processes a single image frame buffer (JPEG/PNG) from client camera, detects hand posture, extracts 21 landmarks, matches against gesture rules, and generates translated audio.

#### Request (Multipart Form-Data)
- `image`: Image file buffer (`UploadFile`)
- `target_language`: Target language string (e.g., `"Kannada"`, `"Hindi"`, `"English"`)

#### Response `200 OK`
```json
{
  "sign_text": "Hello",
  "translated_text": "ನಮಸ್ಕಾರ",
  "audio_url": "/static/audio/a1b2c3d4e5f6.mp3",
  "debug_info": {
    "text": "F:[1, 1, 1, 1] T:Up (Wave)",
    "fingers": [1, 1, 1, 1],
    "thumb": "Up",
    "motion": 0.042,
    "landmarks": [
      { "x": 0.512, "y": 0.724 },
      { "x": 0.485, "y": 0.691 }
    ]
  }
}
```

---

## 4. Synthesize Sentence

### `POST /process_sentence`

Synthesizes multiple tokens into a natural sentence, applies grammar heuristics, translates into target locale, and produces voice audio.

#### Request (`application/json`)
```json
{
  "tokens": ["Hello", "Yes"],
  "target_language": "Kannada"
}
```

#### Response `200 OK`
```json
{
  "original": "Hello! Everything looks good.",
  "translated": "ನಮಸ್ಕಾರ! ಎಲ್ಲವೂ ಸರಿಯಾಗಿದೆ.",
  "audio_url": "/static/audio/7e8f9a0b1c2d.mp3"
}
```

---

## Audio Caching & Pruning Policy

- Generated neural audio files are persisted under `static/audio/`.
- Pre-warmed audio cache eliminates latency on recurrent phrases.
- Least-recently-used audio pruning maintains disk utilization under 150 files.

