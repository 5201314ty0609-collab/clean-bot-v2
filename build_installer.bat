@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title CleanBot v2.0 — 构建安装包

echo.
echo   ╔══════════════════════════════════════════╗
echo   ║  CleanBot v2.0 — 构建 NSIS 安装包       ║
echo   ╚══════════════════════════════════════════╝
echo.
echo   此脚本会先构建 EXE，再封装为标准 Windows 安装程序。
echo.

:: ── Step 1: 构建 EXE ──
echo ── 第 1 步: 构建 CleanBot.exe ──
echo.
call build.bat
if errorlevel 1 (
    echo.
    echo   ✗ EXE 构建失败，无法继续
    pause & exit /b 1
)
echo.

:: ── Step 2: 检查 NSIS ──
echo ── 第 2 步: 检查 NSIS ──
makensis /VERSION >nul 2>&1
if errorlevel 1 (
    echo.
    echo   ⚠️  未安装 NSIS（安装包制作工具）
    echo.
    echo   安装 NSIS:
    echo     1. 访问 https://nsis.sourceforge.io/Download
    echo     2. 下载 nsis-3.x-setup.exe
    echo     3. 安装（一路下一步即可）
    echo     4. 重启命令行窗口
    echo     5. 重新运行 build_installer.bat
    echo.
    echo   便携版 EXE 已生成: dist\CleanBot.exe
    echo   你可以直接分享这个文件（免安装，双击运行）
    echo.
    start https://nsis.sourceforge.io/Download
    pause & exit /b 0
)
makensis /VERSION
echo   ✓ OK
echo.

:: ── Step 3: 检查 LICENSE 文件 ──
echo ── 第 3 步: 准备安装包资源 ──
if not exist LICENSE (
    echo MIT License > LICENSE
    echo   (已创建默认 LICENSE)
)
if not exist installer mkdir installer
echo   ✓ OK
echo.

:: ── Step 4: 构建 NSIS 安装包 ──
echo ── 第 4 步: 构建安装包 ──
echo   正在运行 NSIS...
echo.
makensis /V4 installer.nsi

if errorlevel 1 (
    echo.
    echo   ✗ NSIS 构建失败
    echo   常见原因:
    echo     1. dist\CleanBot.exe 不存在 → 先运行 build.bat
    echo     2. resources\icons\cleanbot.ico 缺失
    echo     3. installer.nsi 路径配置错误
    pause & exit /b 1
)

echo.
echo   ╔══════════════════════════════════════════╗
echo   ║           全部构建完成！                  ║
echo   ║                                          ║
echo   ║  便携版: dist\CleanBot.exe                ║
echo   ║  安装包: installer\CleanBot-Setup.exe     ║
echo   ╚══════════════════════════════════════════╝
echo.
echo   ── 分享建议 ──
echo   给电脑小白:     发 CleanBot-Setup.exe（安装包）
echo   给有 Python 的人: 发整个源码 zip（运行 install.bat 即可）
echo   QQ/微信传输:    把 .exe 改名为 .ex_ 发给对方再改回
echo.
echo   发布到 Gitee:
echo     1. 打开 https://gitee.com/holyty/clean-bot-v2/releases
echo     2. 创建标签 v2.0.0
echo     3. 上传 CleanBot-Setup.exe
echo     4. 用户即可通过应用内更新获取
echo.
pause
