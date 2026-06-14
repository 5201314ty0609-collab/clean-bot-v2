@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   CleanBot v2.0 — 安装程序
echo ========================================
echo.

:: 国内镜像源
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

:: 检查 Python
echo [1/3] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo 错误: 未找到 Python
    echo.
    echo 请先安装 Python：
    echo   1. 访问 https://www.python.org/downloads/
    echo   2. 下载并安装 Python 3.9 或更高版本
    echo   3. 安装时务必勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo    Python 已安装 ✓

:: 安装依赖
echo [2/3] 安装依赖...
echo    这可能需要 1-3 分钟，请耐心等待...
echo.

pip install PyQt6 psutil Pillow -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST% >nul 2>&1

if errorlevel 1 (
    echo    主镜像失败，尝试备用镜像...
    pip install PyQt6 psutil Pillow -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com >nul 2>&1
)

if errorlevel 1 (
    echo.
    echo 错误: 依赖安装失败
    echo.
    echo 请手动运行以下命令：
    echo   pip install PyQt6 psutil Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo.
    pause
    exit /b 1
)

echo    依赖安装完成 ✓

:: 创建桌面快捷方式
echo [3/3] 创建桌面快捷方式...

set "CURRENT_DIR=%~dp0"

(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = oWS.SpecialFolders^("Desktop"^) ^& "\CleanBot v2.0.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%CURRENT_DIR%start.bat"
echo oLink.WorkingDirectory = "%CURRENT_DIR%"
echo oLink.Description = "CleanBot v2.0 — 智能桌面清理机器人"
echo oLink.Save
) > "%TEMP%\create_shortcut.vbs"

cscript //nologo "%TEMP%\create_shortcut.vbs" >nul 2>&1
del "%TEMP%\create_shortcut.vbs" >nul 2>&1

echo    快捷方式创建完成 ✓

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo   使用方法：
echo     双击桌面的 "CleanBot v2.0" 图标即可启动
echo.
echo   功能介绍：
echo     - 系统诊断：检测系统问题
echo     - 文件扫描：清理垃圾文件
echo     - 磁盘监控：实时监控磁盘
echo     - 智能推荐：个性化清理建议
echo.
echo   按任意键退出安装程序...
pause >nul
