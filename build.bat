@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title CleanBot v2.0 — 构建 EXE

echo.
echo   ╔══════════════════════════════════════════╗
echo   ║   CleanBot v2.0 — 构建便携 EXE          ║
echo   ╚══════════════════════════════════════════╝
echo.

:: ── 1. 检查 Python ──
echo [1/6] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ✗ 未找到 Python！
    echo   请安装 Python 3.10+ https://www.python.org/downloads/
    echo   安装时勾选 "Add Python to PATH"
    pause & exit /b 1
)
python --version
echo   ✓ OK
echo.

:: ── 2. 升级 pip ──
echo [2/6] 升级 pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet 2>nul
if errorlevel 1 (
    python -m pip install --upgrade pip --quiet 2>nul
)
echo   ✓ OK
echo.

:: ── 3. 安装依赖 ──
echo [3/6] 安装依赖包...

:: 先尝试清华镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --quiet 2>nul
if errorlevel 1 (
    :: 尝试阿里云镜像
    echo   清华源失败，尝试阿里云...
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com --quiet 2>nul
)
if errorlevel 1 (
    :: 尝试默认源
    echo   阿里云失败，尝试默认源...
    pip install -r requirements.txt --quiet 2>nul
)
if errorlevel 1 (
    echo   ✗ 依赖安装失败！
    echo   请检查网络连接后重试
    pause & exit /b 1
)
echo   ✓ OK
echo.

:: ── 4. 安装 PyInstaller ──
echo [4/6] 检查 PyInstaller...
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo   正在安装 PyInstaller...
    pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet 2>nul
    if errorlevel 1 (
        pip install pyinstaller --quiet 2>nul
    )
    if errorlevel 1 (
        echo   ✗ PyInstaller 安装失败
        pause & exit /b 1
    )
)
pyinstaller --version
echo   ✓ OK
echo.

:: ── 5. 清理旧构建 ──
echo [5/6] 清理旧文件...
if exist build rmdir /s /q build 2>nul
if exist dist  rmdir /s /q dist  2>nul
echo   ✓ OK
echo.

:: ── 6. 打包 ──
echo [6/6] 打包为 CleanBot.exe...
echo   这需要 3-5 分钟，请耐心等待...
echo.

:: 优先使用 spec 文件
pyinstaller cleanbot.spec --clean --noconfirm 2>&1

if errorlevel 1 (
    echo.
    echo   ⚠️  spec 模式失败，尝试命令行模式...
    echo.
    pyinstaller --onefile --windowed ^
        --name "CleanBot" ^
        --icon "resources/icons/cleanbot.ico" ^
        --add-data "config/file_types.json;config" ^
        --add-data "config/update_config.json;config" ^
        --add-data "resources/icons/cleanbot.ico;resources/icons" ^
        --hidden-import "PyQt6" ^
        --hidden-import "PyQt6.QtWidgets" ^
        --hidden-import "PyQt6.QtCore" ^
        --hidden-import "PyQt6.QtGui" ^
        --hidden-import "psutil" ^
        --hidden-import "Pillow" ^
        --hidden-import "send2trash" ^
        --hidden-import "core" ^
        --hidden-import "core.utils" ^
        --hidden-import "core.scanner.file_scanner" ^
        --hidden-import "core.analyzer.smart_analyzer" ^
        --hidden-import "core.cleaner.file_cleaner" ^
        --hidden-import "core.diagnosis.system_diagnosis" ^
        --hidden-import "core.monitor.disk_monitor" ^
        --hidden-import "core.migrator.file_migrator" ^
        --hidden-import "core.migrator.app_migrator" ^
        --hidden-import "core.deep_cleaner.deep_cleaner" ^
        --hidden-import "core.interactive.interactive_cleaner" ^
        --hidden-import "core.ai.recommendation" ^
        --hidden-import "core.ai.dialog_system" ^
        --hidden-import "core.updater" ^
        --hidden-import "ui.dashboard" ^
        --hidden-import "ui.main_window" ^
        --hidden-import "ui.threads" ^
        --hidden-import "ui.styles" ^
        --hidden-import "ui.update_dialog" ^
        --hidden-import "ui.robot.robot_widget" ^
        --hidden-import "ui.robot.character" ^
        --hidden-import "ui.robot.animation" ^
        --hidden-import "ui.robot.expression" ^
        main.py 2>&1
)

if errorlevel 1 (
    echo.
    echo   ✗ 打包失败！
    echo   请截图上面的错误信息并反馈
    pause & exit /b 1
)

echo.
echo   ╔══════════════════════════════════════════╗
echo   ║          构建成功！                       ║
echo   ║                                          ║
echo   ║  输出: dist\CleanBot.exe                  ║
echo   ╚══════════════════════════════════════════╝
echo.
for %%A in (dist\CleanBot.exe) do echo   文件大小: %%~zA bytes
echo.
echo   你可以将 CleanBot.exe 复制到任意 Windows 电脑直接运行
echo.
pause
