@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo CleanBot v2.0 — 国内用户快速安装
echo ========================================
echo.
echo 本脚本使用国内镜像源，无需代理即可安装！
echo.

:: 设置国内镜像源
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

:: 检查 Python
echo [1/4] 检查 Python...
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
echo Python 已安装

:: 升级 pip
echo [2/4] 升级 pip...
python -m pip install --upgrade pip -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST% >nul 2>&1

:: 安装依赖
echo [3/4] 安装依赖（使用清华镜像）...
echo 这可能需要几分钟时间...
echo.

pip install -r requirements.txt -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%

if errorlevel 1 (
    echo.
    echo 清华镜像失败，尝试阿里云镜像...
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
)

if errorlevel 1 (
    echo.
    echo 错误: 安装失败
    echo.
    echo 请手动运行以下命令：
    echo   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    pause
    exit /b 1
)

echo.
echo 依赖安装完成！

:: 生成机器人图片
echo [4/4] 生成机器人图片...
python ui/robot/characters/conan/generate_images.py

if errorlevel 1 (
    echo 警告: 图片生成失败，请手动运行：
    echo   python ui/robot/characters/conan/generate_images.py
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 启动方式：
echo   1. 双击 start.bat 启动主界面
echo   2. 双击 start_robot.bat 启动桌面机器人
echo   3. 命令行: python main.py
echo.
echo 国内镜像源已配置，所有依赖均可正常下载！
echo.
echo 按任意键退出...
pause >nul
