# Sign2Voice

A real-time Sign Language to Voice translation system.

## Quick Start
Double-click **`run.bat`** to start.

## Manual Start
1. Install dependencies:
   ```bash
   pip install fastapi uvicorn mediapipe deep-translator edge-tts opencv-python aiofiles numpy
   ```
2. Run server:
   ```bash
   python main.py
   ```
3. Open `http://localhost:8000`.

## Installation
1. (Recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```


## Architecture
- **Tech Stack**: Python, FastAPI, MediaPipe, EdgeTTS.
- **Frontend**: HTML5, CSS3 (Glassmorphism), Vanilla JS.

