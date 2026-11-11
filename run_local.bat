@echo off
setlocal enabledelayedexpansion

echo ============================================================================
echo   Smart Markdown-to-Print Desktop Publisher - Local Studio Launcher
echo ============================================================================

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating local Python virtual environment ^(.venv^)...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Ensure Python 3.11+ is on PATH.
        pause
        exit /b 1
    )
    echo [2/3] Installing runtime dependencies from requirements.txt...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies from requirements.txt.
        pause
        exit /b 1
    )
)

if not exist "assets\app_icon.ico" (
    echo [INFO] Generating multi-resolution application icon ^(assets\app_icon.ico^)...
    ".venv\Scripts\python.exe" scripts\generate_icon.py
)

echo [3/3] Launching Smart Markdown-to-Print Desktop Publisher...
".venv\Scripts\python.exe" -m src.main
exit /b %ERRORLEVEL%
