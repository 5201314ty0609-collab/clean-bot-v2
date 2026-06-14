@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo CleanBot v2.0 -- Installer (China Mirror)
echo ========================================
echo.

:: Domestic mirror for faster downloads in China
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

:: Check Python
echo [1/5] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [Error] Python not found.
    echo.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

:: Check pip
echo [2/5] Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [Error] pip not found. Please reinstall Python.
    pause
    exit /b 1
)
echo pip available

:: Upgrade pip
echo [3/5] Upgrading pip...
python -m pip install --upgrade pip -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%
if errorlevel 1 (
    echo [Warning] pip upgrade failed, continuing...
)

:: Install dependencies
echo [4/5] Installing dependencies...
echo Using mirror: %PIP_INDEX_URL%
echo This may take a few minutes...
echo.

pip install -r requirements.txt -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%

if errorlevel 1 (
    echo.
    echo [Warning] Primary mirror failed. Trying Aliyun mirror...
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
)

if errorlevel 1 (
    echo.
    echo [Error] Dependency installation failed.
    echo.
    echo Try manually:
    echo   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo   pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
    pause
    exit /b 1
)

echo.
echo Dependencies installed.

:: Create desktop shortcuts
echo [5/5] Creating desktop shortcuts...

:: Main GUI shortcut
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = oWS.SpecialFolders^("Desktop"^) ^& "\CleanBot v2.0.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = WScript.ScriptFullName ^& "\..\start.bat"
echo oLink.WorkingDirectory = WScript.ScriptFullName ^& "\.."
echo oLink.Description = "CleanBot v2.0 -- Smart Desktop Cleanup Robot"
echo oLink.Save
) > create_shortcut.vbs
cscript //nologo create_shortcut.vbs
del create_shortcut.vbs

:: Robot shortcut
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = oWS.SpecialFolders^("Desktop"^) ^& "\CleanBot Robot.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = WScript.ScriptFullName ^& "\..\start_robot.bat"
echo oLink.WorkingDirectory = WScript.ScriptFullName ^& "\.."
echo oLink.Description = "CleanBot Desktop Robot"
echo oLink.Save
) > create_robot_shortcut.vbs
cscript //nologo create_robot_shortcut.vbs
del create_robot_shortcut.vbs

echo Desktop shortcuts created.

echo.
echo ========================================
echo   Installation complete!
echo ========================================
echo.
echo Launch options:
echo   1. Double-click "CleanBot v2.0" on desktop (GUI)
echo   2. Double-click "CleanBot Robot" on desktop (Robot)
echo   3. Double-click start.bat (GUI)
echo   4. Double-click start_robot.bat (Robot)
echo   5. Double-click start_cli.bat (CLI)
echo.
echo No proxy needed -- domestic mirror configured!
echo.
pause
