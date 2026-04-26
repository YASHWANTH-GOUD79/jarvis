@echo off
echo ================================================
echo.
echo    _______  _______  _______  _______  _______ 
echo    ^|      ^|^|      ^|^|      ^|^|      ^|^|      ^|
echo    ^| JARVIS ^|^| SYSTEM ^|^| v3.0  ^|^|        ^|
echo    ^|______^|^|_______^|^|_______^|^|_______^|
echo.
echo ================================================
echo.
echo [JARVIS] Initializing Iron Man AI System...
echo.

cd /d "C:\Users\yashw\OneDrive\Documents\Desktop\new project"

REM Activate virtual environment and start JARVIS
call .venv\Scripts\activate.bat
start "" pythonw.exe main.py
exit