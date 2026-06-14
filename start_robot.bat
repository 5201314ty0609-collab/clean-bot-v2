@echo off
REM CleanBot v2.0 - Desktop Robot Launcher

title CleanBot Robot

where pythonw >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [Error] pythonw not found. Please install Python 3.10+.
    pause
    exit /b 1
)

python -c "import PyQt6" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [Warning] Dependencies not installed. Running install script...
    call "%~dp0install.bat"
)

start "" pythonw "%~dp0main_robot.py"
