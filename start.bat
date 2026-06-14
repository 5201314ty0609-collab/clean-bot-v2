@echo off
REM CleanBot v2.0 - Main GUI Launcher
REM Uses pythonw to avoid console window

title CleanBot v2.0

REM Check Python availability
where pythonw >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [Error] pythonw not found. Please install Python 3.10+.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import PyQt6" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [Warning] Dependencies not installed. Running install script...
    call "%~dp0install.bat"
)

REM Launch GUI with pythonw (no console window)
start "" pythonw "%~dp0main.py"
