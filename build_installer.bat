@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo CleanBot v2.0 — 构建安装包
echo ========================================
echo.

:: 检查 NSIS 是否安装
echo [1/5] 检查 NSIS...
makensis /VERSION >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 NSIS
    echo 请先安装 NSIS: https://nsis.sourceforge.io/Download
    echo 安装后将 NSIS 添加到 PATH 环境变量
    pause
    exit /b 1
)
echo NSIS 可用

:: 检查 Python 是否安装
echo [2/5] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    pause
    exit /b 1
)
echo Python 可用

:: 检查 PyInstaller 是否安装
echo [3/5] 检查 PyInstaller...
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller 未安装，正在安装...
    pip install pyinstaller
)
echo PyInstaller 可用

:: 清理旧的构建文件
echo [4/5] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist installer rmdir /s /q installer
if exist *.spec del *.spec
echo 清理完成

:: 打包程序
echo [5/5] 打包程序...
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
echo 打包完成！

:: 创建安装包目录
if not exist installer mkdir installer

:: 运行 NSIS 构建安装包
echo.
echo 正在构建安装包...
makensis installer.nsi

if errorlevel 1 (
    echo.
    echo 错误: 安装包构建失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 构建完成！
echo ========================================
echo.
echo 安装包位置: installer\CleanBot-Setup.exe
echo 可执行文件: dist\CleanBot.exe
echo.
echo 文件大小:
for %%A in (installer\CleanBot-Setup.exe) do echo   安装包: %%~zA bytes
for %%A in (dist\CleanBot.exe) do echo   程序: %%~zA bytes
echo.
echo 按任意键退出...
pause >nul
