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
    echo Please install Python 3.10+ from https://python.org/downloads
    echo IMPORTANT: Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [2/3] Installing / Verifying Dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Dependency installation reported warnings. Attempting to start server...
)

echo.
echo [3/3] Starting Sign2Voice Server...
echo.
echo Application will start at: http://localhost:8000
echo Web dashboard: http://localhost:8000
echo API Docs:      http://localhost:8000/docs
echo Press Ctrl+C to stop.
echo.

python main.py
pause
