@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo CleanBot v2.0 — 安装程序（国内版）
echo ========================================
echo.

:: 设置国内镜像源
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

:: 检查 Python 是否安装
echo [1/5] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo.
    echo 请先安装 Python 3.9 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    echo 如果已经安装但未添加到 PATH，请手动添加:
    echo   右键 "此电脑" → "属性" → "高级系统设置" → "环境变量"
    echo   在 "系统变量" 中找到 "Path"，添加 Python 安装路径
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

:: 升级 pip
echo [3/5] 升级 pip...
python -m pip install --upgrade pip -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%
if errorlevel 1 (
    echo 警告: pip 升级失败，继续安装...
)

:: 安装依赖
echo [4/5] 安装依赖包...
echo 使用国内镜像源: %PIP_INDEX_URL%
echo 这可能需要几分钟时间...
echo.

pip install -r requirements.txt -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%

if errorlevel 1 (
    echo.
    echo 错误: 依赖安装失败
    echo.
    echo 尝试使用备用镜像源...
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
)

if errorlevel 1 (
    echo.
    echo 错误: 依赖安装失败
    echo.
    echo 请尝试手动安装:
    echo   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo.
    echo 或者:
    echo   pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
    pause
    exit /b 1
)

echo.
echo 依赖安装完成

:: 创建启动脚本
echo [5/5] 创建启动脚本...

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

:: 桌面机器人启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0"
echo start "" pythonw main_robot.py
) > start_robot.bat

echo 启动脚本创建完成

:: 创建桌面快捷方式
echo 创建桌面快捷方式...

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

:: 创建桌面机器人快捷方式
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = oWS.SpecialFolders^("Desktop"^) ^& "\CleanBot 桌面机器人.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = WScript.ScriptFullName ^& "\..\start_robot.bat"
echo oLink.WorkingDirectory = WScript.ScriptFullName ^& "\.."
echo oLink.Description = "CleanBot 桌面机器人 — 可爱的柯南形象"
echo oLink.Save
) > create_robot_shortcut.vbs

cscript //nologo create_robot_shortcut.vbs
del create_robot_shortcut.vbs

echo 桌面快捷方式创建完成

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 启动方式：
echo   1. 双击桌面快捷方式 "CleanBot v2.0" (主界面)
echo   2. 双击桌面快捷方式 "CleanBot 桌面机器人" (桌面机器人)
echo   3. 双击 start.bat (主界面)
echo   4. 双击 start_robot.bat (桌面机器人)
echo.
echo 其他命令：
echo   - start_cli.bat    启动命令行版本
echo   - diagnosis.bat    运行系统诊断
echo.
echo 国内镜像源已配置，无需代理即可使用！
echo.
echo 按任意键退出...
pause >nul
