@echo off
chcp 65001 >nul
title CleanBot — 构建 + 安装
setlocal enabledelayedexpansion

cd /d "%~dp0"
set "HERE=%~dp0"
set "HERE=%HERE:~0,-1%"

echo.
echo   ==========================================
echo     CleanBot v2.0 — 一键构建 + 安装
echo   ==========================================
echo.

:: ── 1. 生成图标 ──
echo [1/4] 生成图标...
python -c "from PIL import Image,ImageDraw;s=256;img=Image.new('RGBA',(s,s),(0,0,0,0));d=ImageDraw.Draw(img);d.ellipse([8,8,s-8,s-8],fill=(37,99,235,255));d.ellipse([52,60,204,192],fill=(255,255,255,255));d.ellipse([72,108,112,152],fill=(37,99,235,255));d.ellipse([144,108,184,152],fill=(37,99,235,255));d.arc([72,140,184,200],0,180,fill=(37,99,235,255),width=7);d.line([128,8,128,44],fill=(255,255,255,255),width=7);d.ellipse([112,0,144,28],fill=(239,68,68,255));img.save('cleanbot.ico',format='ICO',sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])" 2>nul
if exist cleanbot.ico (echo   ✓ cleanbot.ico) else (echo   ✗ 图标生成失败 && pause && exit /b 1)

:: ── 2. 清理 ──
echo [2/4] 清理旧文件...
if exist dist rmdir /s /q dist 2>nul
if exist build rmdir /s /q build 2>nul
echo   ✓ 清理完成

:: ── 3. 打包 ──
echo [3/4] 打包 EXE（3-5 分钟）...
pyinstaller --onedir --windowed --icon=cleanbot.ico --name CleanBot main.py 2>&1
if not exist "dist\CleanBot\CleanBot.exe" (
    echo   ✗ 打包失败
    pause && exit /b 1
)
echo   ✓ EXE 构建完成

:: ── 4. 创建桌面快捷方式 ──
echo [4/4] 创建桌面快捷方式...

:: 最可靠的方式：桌面放 bat 文件
set "DESKTOP=%USERPROFILE%\Desktop"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\桌面"

echo @echo off > "%DESKTOP%\CleanBot.bat"
echo cd /d "%HERE%\dist\CleanBot" >> "%DESKTOP%\CleanBot.bat"
echo start "" CleanBot.exe >> "%DESKTOP%\CleanBot.bat"
echo   ✓ 桌面: CleanBot.bat

:: 同时尝试创建 .lnk（如果 powershell 可用）
powershell -Command "$ws=New-Object -ComObject WScript.Shell;$lnk=$ws.CreateShortcut('%DESKTOP%\CleanBot.lnk');$lnk.TargetPath='%HERE%\dist\CleanBot\CleanBot.exe';$lnk.WorkingDirectory='%HERE%\dist\CleanBot';$lnk.IconLocation='%HERE%\cleanbot.ico,0';$lnk.Save()" 2>nul
if exist "%DESKTOP%\CleanBot.lnk" (
    echo   ✓ 桌面: CleanBot.lnk（带图标）
)

echo.
echo   ==========================================
echo              构建完成！
echo   ==========================================
echo.
echo   EXE 位置: %HERE%\dist\CleanBot\CleanBot.exe
echo   桌面快捷: CleanBot.bat / CleanBot.lnk
echo.
echo   按任意键启动 CleanBot...
pause >nul
start "" "%HERE%\dist\CleanBot\CleanBot.exe"
