@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo CleanBot v2.0 — 打包为独立 EXE
echo ========================================
echo.

:: 检查 Python
echo [1/5] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.10+
    echo 下载: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

:: 安装依赖
echo [2/5] 安装项目依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet
if errorlevel 1 (
    pip install -r requirements.txt --quiet
)
echo.

:: 安装 PyInstaller
echo [3/5] 检查 PyInstaller...
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
)
echo PyInstaller 就绪
echo.

:: 清理旧构建
echo [4/5] 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

:: 打包 (使用 spec 文件, 包含所有核心模块)
echo [5/5] 打包为 CleanBot.exe ...
echo 这可能需要 3-5 分钟...
echo.
pyinstaller cleanbot.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo 错误: 打包失败，尝试不使用 spec 文件...
    pyinstaller --onefile --windowed --name "CleanBot" --icon "resources/icons/cleanbot.ico" ^
        --add-data "config;config" --add-data "resources;resources" ^
        --hidden-import "PyQt6.QtWidgets" --hidden-import "PyQt6.QtCore" --hidden-import "PyQt6.QtGui" ^
        --hidden-import "psutil" --hidden-import "Pillow" ^
        --hidden-import "core" --hidden-import "core.utils" --hidden-import "ui" --hidden-import "ui.dashboard" ^
        --hidden-import "ui.threads" --hidden-import "ui.styles" ^
        --hidden-import "core.scanner.file_scanner" --hidden-import "core.analyzer.smart_analyzer" ^
        --hidden-import "core.cleaner.file_cleaner" --hidden-import "core.diagnosis.system_diagnosis" ^
        --hidden-import "core.monitor.disk_monitor" --hidden-import "core.ai.recommendation" ^
        --hidden-import "core.ai.dialog_system" --hidden-import "ui.robot.robot_widget" ^
        main.py
    if errorlevel 1 (
        echo 错误: 打包失败
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 打包完成!
echo ========================================
echo.
echo 输出文件: dist\CleanBot.exe
echo.
for %%A in (dist\CleanBot.exe) do echo 文件大小: %%~zA bytes
echo.
echo 你可以将 CleanBot.exe 复制到任何 Windows 10/11 电脑上直接运行
echo.
pause
