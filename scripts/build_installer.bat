@echo off
setlocal enabledelayedexpansion

echo ============================================================================
echo   Smart Markdown-to-Print Desktop Publisher - Windows Installer Pipeline
echo ============================================================================

cd /d "%~dp0\.."

call "scripts\build_exe.bat"
if errorlevel 1 (
    echo [ERROR] Standalone EXE build failed. Cannot proceed to installer step.
    exit /b 1
)

set "ISCC_PATH="

if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%ProgramFiles%\Inno Setup 6\ISCC.exe"
) else if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
) else (
    for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do (
        if not defined ISCC_PATH set "ISCC_PATH=%%I"
    )
)

if defined ISCC_PATH (
    echo [INFO] Found Inno Setup Compiler at: "!ISCC_PATH!"
    echo [INFO] Compiling installer\setup.iss...
    "!ISCC_PATH!" "installer\setup.iss"
    if errorlevel 1 (
        echo [ERROR] Inno Setup compilation failed.
        exit /b 1
    )
    echo ============================================================================
    echo   [SUCCESS] Windows Setup Installer generated:
    echo   dist_installer\SmartMarkdownPublisher_Setup.exe
    echo ============================================================================
    exit /b 0
) else (
    echo ============================================================================
    echo   [NOTICE] Inno Setup 6 ^(ISCC.exe^) was not detected on this machine.
    echo   The standalone executable is ready to run directly at:
    echo       dist\SmartMarkdownPublisher.exe
    echo.
    echo   To compile the optional Windows Setup Wizard ^(SmartMarkdownPublisher_Setup.exe^),
    echo   install Inno Setup 6 from: https://jrsoftware.org/isdl.php
    echo   and re-run scripts\build_installer.bat
    echo ============================================================================
    exit /b 0
)
