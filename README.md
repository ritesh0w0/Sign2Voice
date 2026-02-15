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

## Backing Up or Sharing (Zip Method)
To keep a copy or share this project:
1. Delete the `__pycache__` and `venv` folders (if they exist) to keep the file size small.
2. Select all files in the `Sign2Voice` folder.
3. Right-click and choose **Compress to ZIP file**.
4. You can now save this `.zip` file locally or send it to others.

## Architecture
- **Tech Stack**: Python, FastAPI, MediaPipe, EdgeTTS.
- **Frontend**: HTML5, CSS3 (Glassmorphism), Vanilla JS.
