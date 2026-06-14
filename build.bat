@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo CleanBot v2.0 — 打包程序
echo ========================================
echo.

:: 检查 Python 是否安装
echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    pause
    exit /b 1
)
echo Python 可用

:: 检查 PyInstaller 是否安装
echo [2/4] 检查 PyInstaller...
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller 未安装，正在安装...
    pip install pyinstaller
    if errorlevel 1 (
        echo 错误: PyInstaller 安装失败
        pause
        exit /b 1
    )
)
echo PyInstaller 可用

:: 清理旧的构建文件
echo [3/4] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec
echo 清理完成

:: 打包程序
echo [4/4] 打包程序...
echo 这可能需要几分钟时间...
echo.

pyinstaller --onefile --windowed ^
    --name "CleanBot" ^
    --icon "resources/icons/cleanbot.ico" ^
    --add-data "config;config" ^
    --add-data "resources;resources" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "psutil" ^
    main.py

if errorlevel 1 (
    echo.
    echo 错误: 打包失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\CleanBot.exe
echo.
echo 文件大小:
for %%A in (dist\CleanBot.exe) do echo   %%~zA bytes
echo.
echo 按任意键退出...
pause >nul
