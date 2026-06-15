@echo off
chcp 65001 >nul
title CleanBot — 安装
cd /d "%~dp0"

echo.
echo   ╔══════════════════════════════════╗
echo   ║   CleanBot v2.0 — 安装          ║
echo   ║   创建桌面快捷方式               ║
echo   ╚══════════════════════════════════╝
echo.

set "EXE=%~dp0CleanBot.exe"

if not exist "%EXE%" (
    echo   错误：找不到 CleanBot.exe
    echo   请确保 setup.bat 和 CleanBot.exe 在同一文件夹
    pause
    exit /b 1
)

:: 创建桌面 .bat（100%% 可靠）
for %%d in ("%USERPROFILE%\Desktop" "%USERPROFILE%\桌面") do (
    if exist %%d (
        echo @echo off > "%%~d\CleanBot.bat"
        echo cd /d "%~dp0" >> "%%~d\CleanBot.bat"
        echo start "" CleanBot.exe >> "%%~d\CleanBot.bat"
        echo   [OK] 桌面: CleanBot.bat
    )
)

:: 创建 .lnk（带图标）
powershell -Command "$ws=New-Object -ComObject WScript.Shell; $lnk=$ws.CreateShortcut([Environment]::GetFolderPath('Desktop')+'\CleanBot.lnk'); $lnk.TargetPath='%~dp0CleanBot.exe'; $lnk.WorkingDirectory='%~dp0'; $lnk.Save()" 2>nul

echo.
echo   安装完成！双击桌面的 CleanBot 即可启动。
echo.
pause
