@echo off
chcp 65001 >nul
title CleanBot v2.0 — 一键安装
setlocal enabledelayedexpansion

:: 记录安装目录
set "INSTALL_DIR=%~dp0"
set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"

echo.
echo   ╔══════════════════════════════════════════╗
echo   ║   CleanBot v2.0 — 智能桌面清理机器人     ║
echo   ║         一键安装脚本                      ║
echo   ║                                          ║
echo   ║  ⚠ 此脚本需要 Python 3.10+              ║
echo   ║  电脑小白请用 EXE 安装包（免装 Python）   ║
echo   ╚══════════════════════════════════════════╝
echo.
echo   安装目录: %INSTALL_DIR%

:: ── 1. 检查 Python ──
echo [1/4] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ✗ 未找到 Python！
    echo   请安装 Python 3.10+
    echo   https://www.python.org/downloads/
    echo   安装时务必勾选 "Add Python to PATH"
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查 Python 版本号 (需要 >= 3.10)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
for /f "tokens=2 delims=." %%a in ("%PYVER%") do set "PYMINOR=%%a"
if %PYMINOR% LSS 10 (
    echo   ✗ Python %PYVER% 太旧，需要 Python 3.10+
    echo   当前版本: %PYVER%
    echo   请安装 Python 3.10 或更新版本
    echo   https://www.python.org/downloads/
    echo   安装时务必勾选 "Add Python to PATH"
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
echo   Python %PYVER% ✓
echo.

:: ── 2. 安装依赖 ──
echo [2/4] 安装依赖包...
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
    echo   ✗ 依赖安装失败
    pause
    exit /b 1
)
echo   ✓ OK
echo.

:: ── 3. 创建启动方式 ──
echo [3/4] 创建快捷方式...

:: 最可靠的方式：直接在桌面放一个 bat 文件
set "DESKTOP_BAT=%USERPROFILE%\Desktop\CleanBot.bat"
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo start "" python main.py
) > "%DESKTOP_BAT%"
echo   桌面: CleanBot.bat ^(双击启动^)
echo   ^(如果桌面上已经有一个，这个会覆盖它^)

:: 也放一个在安装目录
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo start "" python main.py
) > "%INSTALL_DIR%\start.bat"
echo   安装目录: start.bat ^(备用^)

echo   ✓ OK
echo.

:: ── 4. 打开安装目录并启动 ──
echo [4/4] 启动 CleanBot...

:: 打开安装目录让用户看到
explorer "%INSTALL_DIR%"
timeout /t 1 >nul

echo.
echo   ╔══════════════════════════════════════════╗
echo   ║           安装完成！                      ║
echo   ║                                          ║
echo   ║  桌面: CleanBot.bat (双击启动)            ║
echo   ║  目录: %INSTALL_DIR%                     ║
echo   ║         start.bat (备用启动)              ║
echo   ╚══════════════════════════════════════════╝
echo.
echo   安装目录已自动打开，你可以看到所有文件
echo.
echo   后续启动方法:
echo     1. 桌面双击 CleanBot.bat（推荐）
echo     2. 安装目录双击 start.bat
echo     3. 安装目录运行: python main.py
echo.
echo   按任意键启动 CleanBot...
pause >nul

:: 启动（直接用 python，最可靠）
cd /d "%INSTALL_DIR%"
start "" python main.py
