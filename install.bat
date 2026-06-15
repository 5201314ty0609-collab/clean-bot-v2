@echo off
chcp 65001 >nul
title CleanBot v2.0 — 一键安装

echo.
echo   ╔══════════════════════════════════════════╗
echo   ║     CleanBot v2.0 — 智能桌面清理机器人   ║
echo   ║           一键安装脚本                    ║
echo   ╚══════════════════════════════════════════╝
echo.

:: ── 检查 Python ──
echo [1/3] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo   未检测到 Python
    echo   请先安装 Python 3.10+：
    echo   https://www.python.org/downloads/
    echo   安装时务必勾选 "Add Python to PATH"
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo    ✓ Python 就绪
echo.

:: ── 安装依赖 ──
echo [2/3] 安装依赖包（1-3 分钟）...
set "OK=0"

:: 清华镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --quiet
if not errorlevel 1 set "OK=1"

:: 阿里云镜像
if "%OK%"=="0" (
    echo   清华源失败，尝试阿里云镜像...
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com --quiet
    if not errorlevel 1 set "OK=1"
)

:: 默认源
if "%OK%"=="0" (
    echo   阿里云失败，尝试默认源...
    pip install -r requirements.txt --quiet
    if not errorlevel 1 set "OK=1"
)

if "%OK%"=="0" (
    echo.
    echo   依赖安装失败，请手动运行：
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)
echo    ✓ 依赖安装完成
echo.

:: ── 创建快捷方式 ──
echo [3/3] 创建启动方式...

:: VBS 无窗口启动器
set "VBS=%~dp0start_cleanbot.vbs"
echo Set WshShell = CreateObject("WScript.Shell") > "%VBS%"
echo WshShell.Run "pythonw ""%~dp0main.py""", 0, False >> "%VBS%"

:: 桌面快捷方式
powershell -Command ^
    "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut($ws.SpecialFolders('Desktop') + '\CleanBot.lnk'); $s.TargetPath = '%VBS%'; $s.WorkingDirectory = '%~dp0'; if (Test-Path '%~dp0resources\icons\cleanbot.ico') { $s.IconLocation = '%~dp0resources\icons\cleanbot.ico' }; $s.Save()" 2>nul

:: start.bat 备用
echo @echo off > "%~dp0start.bat"
echo cd /d "%%~dp0" >> "%~dp0start.bat"
echo echo CleanBot v2.0 — 启动中... >> "%~dp0start.bat"
echo start "" pythonw main.py >> "%~dp0start.bat"

echo    ✓ 桌面快捷方式已创建
echo.
echo   ╔══════════════════════════════════════════╗
echo   ║            安装完成!                      ║
echo   ║                                          ║
echo   ║  桌面快捷方式: CleanBot                   ║
echo   ║  备用启动: 双击 start.bat                 ║
echo   ╚══════════════════════════════════════════╝
echo.
choice /c YN /m "是否立即启动 CleanBot" /t 10 /d Y
if errorlevel 2 goto :end
start "" pythonw main.py
echo    CleanBot 已启动!
:end
pause
