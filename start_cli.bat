@echo off
REM CleanBot v2.0 - CLI Launcher

title CleanBot CLI

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [Error] python not found. Please install Python 3.10+.
    pause
    exit /b 1
)

python -c "import psutil" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [Warning] Dependencies not installed. Running install script...
    call "%~dp0install.bat"
)

python "%~dp0main.py" --cli
pause
