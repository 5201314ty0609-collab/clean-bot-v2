@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo CleanBot v2.0 — 安装程序
echo ========================================
echo.

:: 检查 Python 是否安装
echo [1/5] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo 请先安装 Python 3.9 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 找到 Python %PYTHON_VERSION%

:: 检查 pip 是否可用
echo [2/5] 检查 pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 pip
    echo 请重新安装 Python 或手动安装 pip
    pause
    exit /b 1
)
echo pip 可用

:: 安装依赖
echo [3/5] 安装依赖包...
echo 这可能需要几分钟时间...
echo.

pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo 错误: 依赖安装失败
    echo 请检查网络连接或使用国内镜像：
    echo pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    pause
    exit /b 1
)

echo.
echo 依赖安装完成

:: 创建启动脚本
echo [4/5] 创建启动脚本...

:: GUI 启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0"
echo start "" pythonw main.py
) > start.bat

:: CLI 启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0"
echo python main.py --cli
echo pause
) > start_cli.bat

:: 诊断启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0"
echo python main.py --diagnosis
echo pause
) > diagnosis.bat

echo 启动脚本创建完成

:: 创建桌面快捷方式
echo [5/5] 创建桌面快捷方式...

:: 创建 VBScript 来创建快捷方式
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = oWS.SpecialFolders^("Desktop"^) ^& "\CleanBot v2.0.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = WScript.ScriptFullName ^& "\..\start.bat"
echo oLink.WorkingDirectory = WScript.ScriptFullName ^& "\.."
echo oLink.Description = "CleanBot v2.0 — 智能桌面清理机器人"
echo oLink.Save
) > create_shortcut.vbs

cscript //nologo create_shortcut.vbs
del create_shortcut.vbs

echo 桌面快捷方式创建完成

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 启动方式：
echo   1. 双击桌面快捷方式 "CleanBot v2.0"
echo   2. 双击 start.bat
echo   3. 命令行: python main.py
echo.
echo 其他命令：
echo   - start_cli.bat    启动命令行版本
echo   - diagnosis.bat    运行系统诊断
echo.
echo 按任意键退出...
pause >nul
