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
echo   ╚══════════════════════════════════════════╝
echo.
echo   安装目录: %INSTALL_DIR%
echo.

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
python --version
echo   ✓ OK
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

:: 方式A: 直接在桌面放启动脚本 (100%% 可靠)
set "DESKTOP_BAT=%USERPROFILE%\Desktop\CleanBot.bat"
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo echo CleanBot v2.0 — 启动中...
echo start "" pythonw main.py
echo if errorlevel 1 python main.py
) > "%DESKTOP_BAT%"
echo   桌面快捷脚本: %DESKTOP_BAT%

:: 方式B: PowerShell 创建 .lnk (更美观)
set "DESKTOP_LNK=%USERPROFILE%\Desktop\CleanBot.lnk"
set "VBS=%INSTALL_DIR%\start_cleanbot.vbs"

:: VBS 无窗口启动器
(
echo Set Ws = WScript.CreateObject^("WScript.Shell"^)
echo Ws.Run "pythonw ""%INSTALL_DIR%\main.py""", 0, False
) > "%VBS%"

:: 尝试用 PowerShell 创建正规快捷方式
powershell -ExecutionPolicy Bypass -NoProfile -Command ^
    "$ws = New-Object -ComObject WScript.Shell; $lnk = $ws.CreateShortcut('%DESKTOP_LNK%'); $lnk.TargetPath = '%VBS%'; $lnk.WorkingDirectory = '%INSTALL_DIR%'; $lnk.IconLocation = '%INSTALL_DIR%resources\icons\cleanbot.ico,0'; $lnk.Save()" 2>nul

if exist "%DESKTOP_LNK%" (
    echo   桌面图标: CleanBot.lnk
) else (
    :: PowerShell 失败 — 用 mklink 或直接复制 bat 到桌面
    echo   桌面图标创建失败（PowerShell 受限），使用 bat 脚本替代
)

:: 方式C: 在安装目录放启动脚本
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo start "" pythonw main.py
) > "%INSTALL_DIR%\start.bat"

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

:: 启动
cd /d "%INSTALL_DIR%"
start "" pythonw main.py
if errorlevel 1 (
    echo   pythonw 启动失败，尝试 python...
    python main.py
)
