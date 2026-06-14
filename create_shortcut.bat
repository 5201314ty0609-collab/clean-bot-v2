@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo CleanBot v2.0 — 创建桌面快捷方式
echo ========================================
echo.

:: 获取当前目录
set "CURRENT_DIR=%~dp0"

:: 创建 VBScript 来创建快捷方式
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = oWS.SpecialFolders^("Desktop"^) ^& "\CleanBot v2.0.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%CURRENT_DIR%start.bat"
echo oLink.WorkingDirectory = "%CURRENT_DIR%"
echo oLink.Description = "CleanBot v2.0 — 智能桌面清理机器人"
echo oLink.IconLocation = "%CURRENT_DIR%resources\icons\cleanbot.ico,0"
echo oLink.Save
) > "%TEMP%\create_shortcut.vbs"

cscript //nologo "%TEMP%\create_shortcut.vbs"
del "%TEMP%\create_shortcut.vbs"

echo.
echo ✅ 桌面快捷方式创建成功！
echo.
echo 快捷方式位置: 桌面\CleanBot v2.0.lnk
echo.
echo 双击快捷方式即可启动 CleanBot，程序会在任务栏显示。
echo.
echo 按任意键退出...
pause >nul
