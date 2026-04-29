# SPARSH - Complete Integration Guide

## 🚀 Overview

SPARSH is a touchless gesture and voice control system with a modern web-based frontend integrated with a Python backend API.

### Architecture
- **Frontend**: `index.html` - Modern single-page application
- **Backend**: `app.py` - Flask REST API server
- **Modules**: 
  - `sparsh_unified.py` - Gesture recognition module
  - `voice.py` - Voice control module

---

## 📋 Prerequisites

### System Requirements
- Windows 10/11 or Linux/macOS
- Python 3.10 or 3.11 recommended
- Webcam (for gesture control)
- Microphone (for voice control)
- Internet connection (for speech recognition)

### Required Python Packages

Install all dependencies with:
```bash
pip install flask flask-cors opencv-python mediapipe SpeechRecognition PyAudio pyautogui numpy
```

If you are using Python 3.13, install Python 3.11 and create a new virtual environment first. MediaPipe is not reliably available for every Python 3.13 setup yet.

Or run the automatic installer script.

---

## 🔧 Setup Instructions

### Option 1: Automatic Setup (Recommended for Windows)

1. **Double-click** `start_backend.bat`
   - This will automatically install missing packages
   - Starts the Flask server on `http://localhost:5000`

2. **Open the frontend**
   - Open `index.html` in your web browser
   - You should see "✅ Connected to backend server" notification

3. **Use the application**
   - Click "Launch Gesture Control" or "Launch Voice Control"
   - The Python modules will run in separate console windows

### Option 2: Manual Setup (All Platforms)

1. **Install dependencies**
   ```bash
   pip install flask flask-cors opencv-python mediapipe SpeechRecognition PyAudio pyautogui numpy
   ```

2. **Start the backend server**
   ```bash
   python app.py
   ```
   
   Expected output:
   ```
   ==================================================
   SPARSH Backend API Server
   ==================================================
   Base directory: d:\fu
   Starting server on http://localhost:5000
   ==================================================
   ```

3. **Open the frontend**
   - Open `index.html` in your web browser
   - Verify the notification shows "✅ Connected to backend server"

4. **Launch modules**
   - Click the "Launch Gesture Control" or "Launch Voice Control" buttons
   - Each module will open in its own window

---

## 🌐 Web Interface

### Accessing the Frontend

#### With Backend Server Running
1. Open `index.html` in your browser
2. The frontend communicates with the backend at `http://localhost:5000`
3. Click buttons to launch modules

#### Offline/Local Mode
- Simply open `index.html` in any browser
- You'll see the informational sections (Problem, Solution, Features, etc.)
- Launch buttons will show an error (backend not running) - this is expected if you haven't started the server

### Navigation
- **Problem**: Explains the challenges SPARSH solves
- **Solution**: Details about how SPARSH works
- **Features**: Key capabilities of the system
- **How to Use**: Instructions for both gesture and voice control
- **About**: Information about Team MARS and NIRMAAN

---

## 🔌 Backend API Endpoints

### Health Check
```
GET /api/health
```
Returns server status.

### Process Management

#### Launch Gesture Control
```
POST /api/launch/gesture
```
Starts the gesture recognition module.

**Response:**
```json
{
  "success": true,
  "message": "Gesture control launched successfully",
  "pid": 12345,
  "module": "sparsh_unified.py"
}
```

#### Launch Voice Control
```
POST /api/launch/voice
```
Starts the voice control module.

**Response:**
```json
{
  "success": true,
  "message": "Voice control launched successfully",
  "pid": 12346,
  "module": "voice.py"
}
```

#### Get Status
```
GET /api/status
```
Returns the status of both modules.

**Response:**
```json
{
  "gesture_control": {
    "running": true,
    "module": "sparsh_unified.py"
  },
  "voice_control": {
    "running": false,
    "module": "voice.py"
  }
}
```

#### Stop Gesture Control
```
POST /api/stop/gesture
```
Stops the gesture control module.

#### Stop Voice Control
```
POST /api/stop/voice
```
Stops the voice control module.

#### Stop All Modules
```
POST /api/stop/all
```
Stops all running modules.

---

## 🎯 Module Details

### Gesture Control (sparsh_unified.py)

**Features:**
- Hand gesture detection using MediaPipe
- Mouse cursor control with finger tracking
- Click detection based on thumb-index finger distance
- Multiple gesture modes (MOUSE and GESTURE)
- Mode switching with visual feedback

**Controls:**
- **Hand Position**: Move hand to move cursor
- **Thumb-Index Distance**: Close them to click
- **Hold Fist 3s**: Change between MOUSE and GESTURE modes
- **Thumbs Up**: Confirm mode change
- **Thumbs Down**: Cancel mode change
- **Press Q**: Exit application

**Requirements:**
- Webcam
- Good lighting
- Clear hand detection area

### Voice Control (voice.py)

**Features:**
- Speech-to-text using Google Speech Recognition API
- Automatic typing at cursor position
- Voice command support

**Commands:**
- **"type"**: Start voice typing mode
- **"stop typing"**: Pause voice typing
- **"exit"**: Close the application
- **Any other voice input**: Typed as text

**Requirements:**
- Microphone
- Internet connection (for Google API)
- Clear speech for accuracy

---

## 🐛 Troubleshooting

### Issue: Backend server won't start
**Solution:**
1. Check if port 5000 is in use: `netstat -ano | findstr :5000`
2. Stop the process using that port
3. Try starting the server again

### Issue: "Backend server not running" notification
**Solution:**
1. Ensure `app.py` is in the same directory as `index.html`
2. Run `start_backend.bat` or manually start with `python app.py`
3. Verify server shows on `http://localhost:5000/api/health`

### Issue: Modules launch but don't work
**Solution:**
1. Check camera/microphone permissions in Windows Settings
2. Ensure required packages are installed: `pip list | findstr opencv`
3. Test modules directly: `python sparsh_unified.py`

### Issue: Gesture control freezes
**Solution:**
1. Ensure good lighting and clear background
2. Position hand clearly in front of camera
3. Adjust camera distance and angle
4. Check camera driver is up to date

### Issue: Voice recognition doesn't work
**Solution:**
1. Check microphone in Windows Settings → Sound
2. Ensure internet connection (required for Google API)
3. Speak clearly and at normal pace
4. Test microphone with other applications

### Issue: Button clicks show errors
**Solution:**
1. Check browser console (F12 → Console tab) for errors
2. Verify backend server is running and accessible
3. Check Windows Firewall isn't blocking localhost:5000
4. Try opening http://localhost:5000/api/health in browser

---

## 📁 Project Structure

```
d:\fu\
├── index.html              # Frontend UI
├── app.py                  # Backend API server
├── sparsh_unified.py       # Gesture control module
├── voice.py                # Voice control module
├── start_backend.bat       # Windows launcher script
├── run_sparsh_unified.bat  # Original gesture launcher
└── INTEGRATION_GUIDE.md    # This file
```

---

## 🚀 Advanced Usage

### Running on Different Port
Edit `app.py` and change:
```python
app.run(
    host='localhost',
    port=5001,  # Change this
    debug=False
)
```

Then update `index.html`:
```javascript
const API_BASE_URL = 'http://localhost:5001/api';
```

### Running on Network
Allow network access by changing in `app.py`:
```python
app.run(
    host='0.0.0.0',  # Allow external connections
    port=5000,
    debug=False
)
```

Then access from another machine using the computer's IP:
```
http://192.168.x.x:5000
```

### Custom Logging
Add logging to `app.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

---

## 📚 Dependencies Explained

| Package | Purpose | Installation |
|---------|---------|--------------|
| Flask | Web framework | `pip install flask` |
| Flask-CORS | Cross-origin requests | `pip install flask-cors` |
| OpenCV | Computer vision | `pip install opencv-python` |
| MediaPipe | Hand detection | `pip install mediapipe` |
| SpeechRecognition | Voice recognition | `pip install SpeechRecognition` |
| PyAudio | Microphone input backend for SpeechRecognition | `pip install PyAudio` |
| PyAutoGUI | Mouse/keyboard control | `pip install pyautogui` |
| NumPy | Numerical computing | `pip install numpy` |

---

## 🔐 Security Notes

1. **Local Network Only**: The server runs on localhost by default for security
2. **CORS Enabled**: Frontend can communicate with backend
3. **Process Management**: Server properly cleans up child processes on exit
4. **No Authentication**: For local development only - add authentication for production

---

## 📝 Logging and Debugging

### Enable Debug Mode in Flask
```python
app.run(debug=True)  # Not recommended for production
```

### Check Running Processes
Windows:
```bash
tasklist | findstr python
```

### View Server Logs
The server prints all launch/stop events to console for debugging.

---

## 🎓 Learning Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **MediaPipe Hand Tracking**: https://google.github.io/mediapipe/solutions/hands
- **Speech Recognition API**: https://github.com/Uberi/speech_recognition
- **OpenCV Tutorials**: https://docs.opencv.org/

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review console output for error messages
3. Check browser developer tools (F12)
4. Verify all dependencies are installed

---

## 🎉 You're Ready!

Your SPARSH system is now fully integrated:
- ✅ Frontend: Beautiful web interface
- ✅ Backend: Robust API server
- ✅ Gesture Control: Hand tracking
- ✅ Voice Control: Speech recognition

Start using SPARSH:
```bash
# Step 1: Start the backend
python app.py
# Or on Windows: start_backend.bat

# Step 2: Open index.html in your browser

# Step 3: Click "Launch Gesture Control" or "Launch Voice Control"

# Enjoy hands-free computing!
```

---

**Made with ❤️ by Team MARS for NIRMAAN **
