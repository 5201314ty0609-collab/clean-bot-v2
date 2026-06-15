; CleanBot v2.0 — NSIS 安装包脚本
; 用于创建 Windows 安装程序

!include "MUI2.nsh"
!include "FileFunc.nsh"

; 定义常量
!define PRODUCT_NAME "CleanBot"
!define PRODUCT_VERSION "3.0.0"
!define PRODUCT_PUBLISHER "PHOENIX"
!define PRODUCT_WEB_SITE "https://gitee.com/holyty/clean-bot-v2"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\CleanBot.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; 安装包属性
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "installer\CleanBot-Setup.exe"
InstallDir "$PROGRAMFILES\${PRODUCT_NAME}"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show
RequestExecutionLevel admin

; 界面设置
!define MUI_ABORTWARNING
!define MUI_ICON "resources\icons\cleanbot.ico"
!define MUI_UNICON "resources\icons\cleanbot.ico"

; 安装页面
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; 卸载页面
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; 语言设置
!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "English"

; 安装程序段
Section "CleanBot 主程序" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite on

  ; 复制主程序文件夹（onedir 模式）
  File /r "dist\CleanBot\*.*"
  File "LICENSE"
  File "README.md"

  ; 创建卸载脚本
  FileOpen $0 "$INSTDIR\uninstall.bat" w
  FileWrite $0 '@echo off$\r$\n'
  FileWrite $0 'cd /d "%~dp0"$\r$\n'
  FileWrite $0 'rmdir /s /q "$INSTDIR"$\r$\n'
  FileClose $0

  ; 创建桌面快捷方式
  CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\CleanBot.exe"

  ; 创建开始菜单快捷方式
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\CleanBot.exe"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\卸载 ${PRODUCT_NAME}.lnk" "$INSTDIR\uninstall.exe"

  ; 写入注册表
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\CleanBot.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\CleanBot.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"

  ; 获取文件大小
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "EstimatedSize" "$0"

  ; 写入卸载程序
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; 卸载程序段
Section Uninstall
  ; 删除文件
  Delete "$INSTDIR\CleanBot.exe"
  Delete "$INSTDIR\LICENSE"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\start.bat"
  Delete "$INSTDIR\uninstall.bat"
  Delete "$INSTDIR\uninstall.exe"

  ; 删除目录
  RMDir /r "$INSTDIR\config"
  RMDir /r "$INSTDIR\resources"
  RMDir "$INSTDIR"

  ; 删除快捷方式
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"

  ; 删除注册表项
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  ; 删除用户数据（可选）
  MessageBox MB_YESNO "是否删除用户数据？" IDNO SkipUserData
    RMDir /r "$PROFILE\CleanBot"
  SkipUserData:

  SetAutoClose true
SectionEnd

; 安装前检查
Function .onInit
  ; 检查是否已安装
  ReadRegStr $0 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString"
  StrCmp $0 "" done

  MessageBox MB_YESNO|MB_ICONQUESTION "已安装 ${PRODUCT_NAME}，是否先卸载旧版本？" IDYES uninst
  Abort

  uninst:
    ClearErrors
    ExecWait '$0 _?=$INSTDIR'

  done:
FunctionEnd
