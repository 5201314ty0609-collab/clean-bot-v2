@echo off
chcp 65001 >nul
title CleanBot — 安装桌面快捷方式
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo   ╔════════════════════════════════════╗
echo   ║  CleanBot v2.0 — 安装           ║
echo   ║  创建桌面快捷方式，方便下次启动   ║
echo   ╚════════════════════════════════════╝
echo.

set "EXE=%~dp0CleanBot.exe"
if not exist "%EXE%" (
    echo   [错误] 找不到 CleanBot.exe
    echo   请确保 setup.bat 和 CleanBot.exe 在同一个文件夹里
    echo   当前文件夹: %~dp0
    pause
    exit /b 1
)

:: ── 1. 找桌面路径（中英文 Windows 兼容） ──
set "DESKTOP="
for %%d in ("%USERPROFILE%\Desktop" "%USERPROFILE%\桌面" "%HOMEDRIVE%%HOMEPATH%\Desktop" "%HOMEDRIVE%%HOMEPATH%\桌面") do (
    if exist %%d (
        set "DESKTOP=%%~d"
    )
)
if "%DESKTOP%"=="" (
    echo   [错误] 找不到桌面文件夹
    echo   请手动创建快捷方式：右键 CleanBot.exe → 发送到 → 桌面快捷方式
    pause
    exit /b 1
)

:: ── 2. 创建 .bat 快捷方式（最可靠，任何 Windows 都能用） ──
(
echo @echo off
echo cd /d "%~dp0"
echo start "" "%~dp0CleanBot.exe"
) > "%DESKTOP%\CleanBot.bat"
echo   [OK] 桌面快捷方式已创建: CleanBot.bat

:: ── 3. 创建 .lnk 快捷方式（带图标，更美观） ──
powershell -Command "$ws=New-Object -ComObject WScript.Shell;$lnk=$ws.CreateShortcut('%DESKTOP%\CleanBot.lnk');$lnk.TargetPath='%EXE%';$lnk.WorkingDirectory='%~dp0';$lnk.Description='CleanBot - 智能桌面清理机器人';$lnk.Save()" 2>nul
if exist "%DESKTOP%\CleanBot.lnk" (
    echo   [OK] 桌面图标已创建: CleanBot.lnk
) else (
    echo   [提示] 图标创建失败，使用 CleanBot.bat 双击启动即可
)

echo.
echo   ╔════════════════════════════════════╗
echo   ║         安装完成！               ║
echo   ║                                  ║
echo   ║  双击桌面的 CleanBot 即可启动     ║
echo   ║  以后不需要再运行这个 setup.bat  ║
echo   ╚════════════════════════════════════╝
echo.

:: 询问是否立即启动
set /p START="是否立即启动 CleanBot？(Y/N): "
if /i "%START%"=="Y" start "" "%EXE%"

pause
