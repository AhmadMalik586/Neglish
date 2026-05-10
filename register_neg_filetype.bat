@echo off
setlocal

REM Registers .neg files with a custom icon and neglish.exe launcher.
REM Run as Administrator for full system-wide association.

set "EXE_PATH=%~dp0dist\neglish.exe"
set "ICO_PATH=%~dp0negextension.ico"

if not exist "%EXE_PATH%" (
  echo [ERROR] Missing "%EXE_PATH%".
  echo Build runtime first: build_neg_exe.bat main.neg neglish
  exit /b 1
)

if not exist "%ICO_PATH%" (
  echo [ERROR] Missing "%ICO_PATH%".
  echo Put your icon file as negextension.ico in project root.
  exit /b 1
)

reg add "HKCU\Software\Classes\.neg" /ve /d "NeglishFile" /f >nul
reg add "HKCU\Software\Classes\NeglishFile" /ve /d "Neglish Program" /f >nul
reg add "HKCU\Software\Classes\NeglishFile\DefaultIcon" /ve /d "\"%ICO_PATH%\",0" /f >nul
reg add "HKCU\Software\Classes\NeglishFile\shell\open\command" /ve /d "\"%EXE_PATH%\" \"%%1\"" /f >nul

echo [OK] .neg file association installed for current user.
echo You may need to restart Explorer or sign out/in to refresh icons.
exit /b 0
