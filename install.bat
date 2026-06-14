@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo CleanBot v2.0 — 安装程序
echo ========================================
echo.

:: 国内镜像源
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

:: 检查 Python
echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo.
    echo 请先安装 Python 3.9 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 找到 Python %PYTHON_VERSION%

:: 检查 pip
echo [2/4] 检查 pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 pip
    echo 请重新安装 Python 或手动安装 pip
    pause
    exit /b 1
)
echo pip 可用

:: 安装依赖
echo [3/4] 安装依赖包...
echo 使用国内镜像源: %PIP_INDEX_URL%
echo 这可能需要几分钟时间...
echo.

pip install -r requirements.txt -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%

if errorlevel 1 (
    echo.
    echo 主镜像失败，尝试备用镜像...
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
)

if errorlevel 1 (
    echo.
    echo 错误: 依赖安装失败
    echo.
    echo 请手动运行:
    echo   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    pause
    exit /b 1
)

echo.
echo 依赖安装完成

:: 创建桌面快捷方式
echo [4/4] 创建桌面快捷方式...

:: 获取当前目录
set "CURRENT_DIR=%~dp0"

:: 创建主快捷方式
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = oWS.SpecialFolders^("Desktop"^) ^& "\CleanBot v2.0.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%CURRENT_DIR%start.bat"
echo oLink.WorkingDirectory = "%CURRENT_DIR%"
echo oLink.Description = "CleanBot v2.0 — 智能桌面清理机器人"
echo oLink.Save
) > "%TEMP%\create_shortcut.vbs"

cscript //nologo "%TEMP%\create_shortcut.vbs"
del "%TEMP%\create_shortcut.vbs"

echo 桌面快捷方式创建完成

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 启动方式:
echo   1. 双击桌面快捷方式 "CleanBot v2.0"
echo   2. 双击 start.bat
echo   3. 命令行: python main.py
echo.
echo 程序启动后会在任务栏显示，可以选择不同模式。
echo.
echo 按任意键退出...
pause >nul
