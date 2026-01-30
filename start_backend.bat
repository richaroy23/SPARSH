@echo off
REM SPARSH Backend Server Launcher
REM This script starts the Flask backend server

echo.
echo ================================================
echo    SPARSH Backend API Server Launcher
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo [INFO] Python detected
python --version

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] Flask is not installed. Installing required packages...
    echo.
    pip install flask flask-cors
    if errorlevel 1 (
        echo [ERROR] Failed to install required packages
        pause
        exit /b 1
    )
)

REM Check if required packages are installed
python -c "import cv2" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] OpenCV is not installed. Installing required packages...
    echo.
    pip install opencv-python
)

python -c "import mediapipe" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] MediaPipe is not installed. Installing required packages...
    echo.
    pip install mediapipe
)

python -c "import speech_recognition" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] SpeechRecognition is not installed. Installing required packages...
    echo.
    pip install SpeechRecognition
)

REM Start the server
echo.
echo [INFO] Starting SPARSH Backend Server...
echo.
echo ================================================
echo Press Ctrl+C to stop the server
echo ================================================
echo.

python app.py

REM Show error if server fails to start
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start the server
    echo.
    pause
    exit /b 1
)
