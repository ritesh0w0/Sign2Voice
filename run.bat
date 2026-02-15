@echo off
TITLE Sign2Voice Launcher
echo ====================================================
echo              Sign2Voice - AI Sign Language System
echo ====================================================
echo.

echo [1/3] Checking Python Environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your PATH.
    echo.
    echo Please install Python from https://python.org/downloads
    echo IMPORTANT: Check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b
)

echo [2/3] Installing Dependencies...
python -m pip install "protobuf==3.20.3" fastapi uvicorn "mediapipe==0.10.9" deep-translator edge-tts opencv-python aiofiles numpy python-multipart
if %errorlevel% neq 0 (
    echo [WARNING] There was an issue installing dependencies. Attempting to continue...
)

echo [3/3] Starting Server...
echo.
echo Application will start at: http://localhost:8000
echo Ctrl+C to stop.
echo.
python main.py
pause
