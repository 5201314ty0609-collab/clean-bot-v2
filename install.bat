@echo off
chcp 65001 >nul
title CleanBot v2.0 — 一键安装
setlocal enabledelayedexpansion

set "INSTALL_DIR=%~dp0"
set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"

echo.
echo   ╔══════════════════════════════════════════╗
echo   ║   CleanBot v2.0 — 智能桌面清理机器人     ║
echo   ║         一键安装脚本                      ║
echo   ╚══════════════════════════════════════════╝
echo.
echo   安装目录: %INSTALL_DIR%

:: ── 1. 检查 Python ──
echo [1/3] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ✗ 未找到 Python！请安装 Python 3.10+
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
for /f "tokens=2 delims=." %%a in ("%PYVER%") do set "PYMINOR=%%a"
if %PYMINOR% LSS 10 (
    echo   ✗ Python %PYVER% 太旧，需要 3.10+
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
echo   Python %PYVER% ✓
echo.

:: ── 2. 安装依赖 ──
echo [2/3] 安装依赖包...
set "OK=0"
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --quiet 2>nul
if not errorlevel 1 set "OK=1"
if "%OK%"=="0" (
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com --quiet 2>nul
    if not errorlevel 1 set "OK=1"
)
if "%OK%"=="0" (
    pip install -r requirements.txt --quiet 2>nul
    if not errorlevel 1 set "OK=1"
)
if "%OK%"=="0" (
    echo   ✗ 依赖安装失败，请检查网络
    pause
    exit /b 1
)
echo   ✓ OK
echo.

:: ── 3. 创建桌面快捷方式 + 启动 ──
echo [3/3] 创建桌面快捷方式...

:: 检测实际桌面路径（中文 Windows 是"桌面"）
set "DESKTOP_FOUND="
for %%d in ("%USERPROFILE%\Desktop" "%USERPROFILE%\桌面" "%USERPROFILE%\desktop") do (
    if exist %%d (
        set "DESKTOP_FOUND=%%~d"
    )
)
if "%DESKTOP_FOUND%"=="" set "DESKTOP_FOUND=%USERPROFILE%\Desktop"

:: 在桌面放启动脚本
set "DESKTOP_BAT=%DESKTOP_FOUND%\CleanBot.bat"
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo python main.py
echo pause
) > "%DESKTOP_BAT%"

:: 在安装目录放启动脚本
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo python main.py
echo pause
) > "%INSTALL_DIR%\start.bat"

echo   ✓ 桌面: CleanBot.bat
echo   ✓ 安装目录: start.bat
echo.
echo   ╔══════════════════════════════════════════╗
echo   ║           安装完成！                      ║
echo   ║                                          ║
echo   ║  双击桌面的 CleanBot.bat 启动              ║
echo   ║  或双击本目录的 start.bat                  ║
echo   ╚══════════════════════════════════════════╝
echo.
echo   正在启动 CleanBot...
cd /d "%INSTALL_DIR%"
python main.py
