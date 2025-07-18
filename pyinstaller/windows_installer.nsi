; Photo Organizer Windows Installer Script
; NSIS (Nullsoft Scriptable Install System) script for creating a Windows installer

; Define constants
!define PRODUCT_NAME "Photo Organizer"
!define PRODUCT_VERSION "0.1.0"
!define PRODUCT_PUBLISHER "Photo Organizer Team"
!define PRODUCT_WEB_SITE "https://github.com/example/photo-organizer"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\photo-organizer.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; Include modern UI
!include "MUI2.nsh"

; Set compression
SetCompressor lzma

; Set metadata
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "..\dist\PhotoOrganizer-${PRODUCT_VERSION}-Setup.exe"
InstallDir "$PROGRAMFILES\Photo Organizer"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "..\pyinstaller\icon.ico"
!define MUI_UNICON "..\pyinstaller\icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "..\pyinstaller\welcome.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "..\pyinstaller\welcome.bmp"

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; License page
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"

; Directory page
!insertmacro MUI_PAGE_DIRECTORY

; Instfiles page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\photo-organizer.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

; Installation
Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  
  ; Copy all files from the dist directory
  File /r "..\dist\photo-organizer\*.*"
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\Photo Organizer"
  CreateShortCut "$SMPROGRAMS\Photo Organizer\Photo Organizer.lnk" "$INSTDIR\photo-organizer.exe"
  CreateShortCut "$DESKTOP\Photo Organizer.lnk" "$INSTDIR\photo-organizer.exe"
SectionEnd

; Post-installation
Section -Post
  ; Register application
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\photo-organizer.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\photo-organizer.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninst.exe"
SectionEnd

; Uninstallation
Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  ; Remove files and directories
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\photo-organizer.exe"
  RMDir /r "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\Photo Organizer\Photo Organizer.lnk"
  Delete "$DESKTOP\Photo Organizer.lnk"
  RMDir "$SMPROGRAMS\Photo Organizer"
  
  ; Remove registry entries
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd