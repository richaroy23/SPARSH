@echo off
echo ========================================
echo       SPARSH - Unified Gesture Control
echo ========================================
echo.
echo Starting unified application...
echo Default mode: MOUSE CONTROL
echo.
echo HOW TO USE:
echo -----------
echo MOUSE MODE:
echo - Point index finger to move cursor
echo - Pinch thumb+index to click
echo.
echo GESTURE MODE:  
echo - 1 finger = RIGHT arrow
echo - 2 fingers = LEFT arrow
echo - 3 fingers = UP arrow
echo - 4 fingers = DOWN arrow
echo - 5 fingers = SPACE
echo.
echo MODE SWITCHING:
echo - Hold FIST for 3 seconds
echo - THUMBS UP = Confirm change
echo - THUMBS DOWN = Cancel
echo.
echo Press 'q' in the video window to quit
echo ========================================
echo.
cd /d "C:\Users\richa\OneDrive\Desktop\SPARSH\project"
"C:\Users\richa\OneDrive\Desktop\SPARSH\project\handtracking\.venv\Scripts\python.exe" sparsh_unified.py
pause