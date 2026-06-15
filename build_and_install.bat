@echo off
chcp 65001 >nul
title CleanBot — 一键构建
cd /d "%~dp0"
set "HERE=%~dp0"
set "HERE=%HERE:~0,-1%"

echo.
echo   ==========================================
echo     CleanBot v2.0 — 构建 EXE + 桌面快捷方式
echo   ==========================================
echo.

:: ── 1. 生成图标 ──
echo [1/4] 生成图标...
python -c "from PIL import Image,ImageDraw;s=256;img=Image.new('RGBA',(s,s),(0,0,0,0));d=ImageDraw.Draw(img);d.ellipse([8,8,s-8,s-8],fill=(37,99,235,255));d.ellipse([52,60,204,192],fill=(255,255,255,255));d.ellipse([72,108,112,152],fill=(37,99,235,255));d.ellipse([144,108,184,152],fill=(37,99,235,255));d.arc([72,140,184,200],0,180,fill=(37,99,235,255),width=7);d.line([128,8,128,44],fill=(255,255,255,255),width=7);d.ellipse([112,0,144,28],fill=(239,68,68,255));img.save('cleanbot.ico',format='ICO',sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])" 2>nul
if exist cleanbot.ico (echo   [OK] 图标) else (echo   [FAIL] 图标生成失败 && pause && exit /b 1)

:: ── 2. 清理 ──
echo [2/4] 清理旧文件...
if exist dist rmdir /s /q dist 2>nul
if exist build rmdir /s /q build 2>nul
echo   [OK] 清理完成

:: ── 3. 打包 ──
echo [3/4] 打包 EXE（等待 3-5 分钟）...
pyinstaller --onedir --windowed --icon=cleanbot.ico --name CleanBot main.py 2>&1 > build_log.txt
if not exist "dist\CleanBot\CleanBot.exe" (
    echo   [FAIL] 打包失败！查看 build_log.txt
    type build_log.txt | findstr /i "error traceback"
    pause && exit /b 1
)
echo   [OK] EXE 构建完成

:: ── 3.5 复制 setup.bat 到发布文件夹 ──
copy /y setup.bat "dist\CleanBot\setup.bat" >nul 2>&1
echo   [OK] setup.bat 已复制到发布文件夹

:: ── 4. 桌面快捷方式 ──
echo [4/4] 创建桌面快捷方式...

:: .bat 快捷方式（100%% 可靠）
for %%d in ("%USERPROFILE%\Desktop" "%USERPROFILE%\桌面") do (
    if exist %%d (
        echo @echo off > "%%~d\CleanBot.bat"
        echo cd /d "%HERE%\dist\CleanBot" >> "%%~d\CleanBot.bat"
        echo start "" CleanBot.exe >> "%%~d\CleanBot.bat"
        echo   [OK] 桌面: CleanBot.bat
    )
)

:: .lnk 快捷方式（带图标）
powershell -Command "$ws=New-Object -ComObject WScript.Shell;$lnk=$ws.CreateShortcut([Environment]::GetFolderPath('Desktop')+'\CleanBot.lnk');$lnk.TargetPath='%HERE%\dist\CleanBot\CleanBot.exe';$lnk.WorkingDirectory='%HERE%\dist\CleanBot';$lnk.IconLocation='%HERE%\cleanbot.ico,0';$lnk.Save()" 2>nul
if exist "%USERPROFILE%\Desktop\CleanBot.lnk" echo   [OK] 桌面: CleanBot.lnk（带图标）

echo.
echo   ==========================================
echo              构建完成！
echo   ==========================================
echo.
echo   双击桌面的 CleanBot 即可启动
echo.
pause
