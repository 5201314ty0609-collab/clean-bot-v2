@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo CleanBot v2.0 — 构建安装包
echo ========================================
echo.

:: Step 1: Build EXE first
echo [1/6] 构建 CleanBot.exe...
call build.bat
if errorlevel 1 (
    echo 错误: EXE 构建失败
    pause
    exit /b 1
)
echo.

:: Step 2: Check NSIS
echo [2/6] 检查 NSIS...
makensis /VERSION >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  NSIS 未安装，无法创建安装包
    echo.
    echo 安装 NSIS:
    echo   1. 访问 https://nsis.sourceforge.io/Download
    echo   2. 下载并安装 NSIS
    echo   3. 将 NSIS 安装目录添加到 PATH
    echo      (通常是 C:\Program Files (x86)\NSIS\)
    echo.
    echo 跳过安装包构建，EXE 文件已生成在 dist\ 目录
    echo.
    pause
    exit /b 0
)
echo NSIS 可用
echo.

:: Step 3: Prepare installer directory
echo [3/6] 准备安装包目录...
if not exist installer mkdir installer
echo.

:: Step 4: Copy README to LICENSE if missing
echo [4/6] 检查授权文件...
if not exist LICENSE echo MIT License > LICENSE
echo.

:: Step 5: Build NSIS installer
echo [5/6] 构建 NSIS 安装包...
makensis /V4 installer.nsi
if errorlevel 1 (
    echo.
    echo 错误: NSIS 构建失败
    echo 请检查 installer.nsi 中的路径和配置
    pause
    exit /b 1
)
echo.

:: Step 6: Done
echo [6/6] 构建完成!
echo.
echo ========================================
echo 输出文件
echo ========================================
echo.
echo  便携版: dist\CleanBot.exe
for %%A in (dist\CleanBot.exe) do echo          大小: %%~zA bytes
echo.
if exist "installer\CleanBot-Setup.exe" (
    echo  安装包: installer\CleanBot-Setup.exe
    for %%A in (installer\CleanBot-Setup.exe) do echo          大小: %%~zA bytes
)
echo.
echo ========================================
echo 分发方式
echo ========================================
echo.
echo  方案 A: 直接发送 CleanBot.exe 给用户
echo          双击即可运行，无需安装
echo.
echo  方案 B: 发送 CleanBot-Setup.exe 安装包
echo          安装到 Program Files，创建桌面快捷方式
echo.
pause
