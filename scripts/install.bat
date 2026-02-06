@echo off
echo ========================================
echo   AI Agent - Windows Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.10+
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found

REM Check Ollama
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [WARN] Ollama not found. Installing...
    winget install Ollama.Ollama
    echo [INFO] Please restart this script after Ollama installation
    pause
    exit /b 1
)
echo [OK] Ollama found

REM Create virtual environment
echo [INFO] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt

REM Download model
echo [INFO] Downloading Qwen model (this may take a while)...
ollama pull qwen2.5-coder:3b-instruct-q4_K_M

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Run the agent with:
echo   venv\Scripts\activate
echo   python scripts\run_agent.py
echo.
pause
