@echo off
setlocal enabledelayedexpansion

echo ============================================================================
echo   Smart Markdown-to-Print Desktop Publisher - Standalone EXE Builder
echo ============================================================================

cd /d "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment .venv not found. Run run_local.bat first.
    exit /b 1
)

call ".venv\Scripts\activate.bat"

echo [1/4] Running automated unit test suite ^(pytest^)...
".venv\Scripts\python.exe" -m pytest
if errorlevel 1 (
    echo [ERROR] Unit tests failed. Aborting executable build.
    exit /b 1
)

echo [2/4] Ensuring multi-resolution application icon ^(assets\app_icon.ico^)...
".venv\Scripts\python.exe" scripts\generate_icon.py
if errorlevel 1 (
    echo [ERROR] Icon generation failed.
    exit /b 1
)

echo [3/4] Compiling standalone Windows executable via PyInstaller...
".venv\Scripts\pyinstaller.exe" --clean --noconfirm build_windows.spec
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    exit /b 1
)

echo [4/4] Verifying output artifact...
if not exist "dist\SmartMarkdownPublisher.exe" (
    echo [ERROR] Expected output dist\SmartMarkdownPublisher.exe was not found!
    exit /b 1
)

echo ============================================================================
echo   [SUCCESS] Standalone executable built: dist\SmartMarkdownPublisher.exe
echo ============================================================================
exit /b 0
