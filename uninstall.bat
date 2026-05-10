@echo off
:: uninstall.bat — Remove Neglish from PATH and delete install files

setlocal ENABLEDELAYEDEXPANSION

set "INSTALL_DIR=%LOCALAPPDATA%\Neglish"

echo Uninstalling Neglish...

:: Remove from PATH
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "CUR_PATH=%%B"
set "NEW_PATH="
for %%P in ("!CUR_PATH:;=" "!") do (
  set "SEG=%%~P"
  if /i not "!SEG!"=="%INSTALL_DIR%" (
    if "!NEW_PATH!"=="" (set "NEW_PATH=!SEG!") else (set "NEW_PATH=!NEW_PATH!;!SEG!")
  )
)
reg add "HKCU\Environment" /v Path /t REG_EXPAND_SZ /d "!NEW_PATH!" /f >nul
echo [1/2] Removed from PATH.

:: Delete install directory
if exist "%INSTALL_DIR%" (
  rmdir /S /Q "%INSTALL_DIR%"
  echo [2/2] Deleted %INSTALL_DIR%
) else (
  echo [2/2] Install directory not found (already removed?).
)

echo.
echo  Neglish uninstalled. Open a new terminal for the PATH change to take effect.
endlocal
