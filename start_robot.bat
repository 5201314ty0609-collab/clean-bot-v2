@echo off
chcp 65001 >nul
title CleanBot v2.0 — 桌面机器人

echo ========================================
echo   CleanBot v2.0 — 桌面机器人模式
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: 启动机器人
echo 正在启动桌面机器人...
echo.
python -c "from ui.robot.robot_widget import main; main()"

pause
