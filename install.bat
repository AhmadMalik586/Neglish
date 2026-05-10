@echo off
:: install.bat — Add Neglish to your system PATH
:: Run this once after building neglish.exe
:: Usage: install.bat            (installs from dist\neglish.exe)
::        install.bat <path>     (installs from a custom path)

setlocal ENABLEDELAYEDEXPANSION

set "EXE_SRC=%~dp0dist\neglish.exe"
if not "%~1"=="" set "EXE_SRC=%~1"

if not exist "%EXE_SRC%" (
  echo [ERROR] neglish.exe not found at: %EXE_SRC%
  echo Build it first with:  pyinstaller neglish.spec
  echo Or run:               build_neg_exe.bat
  exit /b 1
)

echo [1/3] Installing Neglish...
set "INSTALL_DIR=%LOCALAPPDATA%\Neglish"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

copy /Y "%EXE_SRC%" "%INSTALL_DIR%\neglish.exe" >nul
if errorlevel 1 (
  echo [ERROR] Failed to copy neglish.exe
  exit /b 1
)

:: Copy stdlib if it exists next to the exe
set "STDLIB_SRC=%~dp0stdlib"
if exist "%STDLIB_SRC%" (
  xcopy /E /I /Y "%STDLIB_SRC%" "%INSTALL_DIR%\stdlib" >nul
  echo [2/3] Standard library copied.
) else (
  echo [2/3] No stdlib directory found (skipped).
)

echo [3/3] Adding to user PATH...
:: Read current user PATH from registry
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "CUR_PATH=%%B"

:: Check if already in PATH
echo !CUR_PATH! | findstr /i /c:"%INSTALL_DIR%" >nul
if errorlevel 1 (
  if "!CUR_PATH!"=="" (
    set "NEW_PATH=%INSTALL_DIR%"
  ) else (
    set "NEW_PATH=!CUR_PATH!;%INSTALL_DIR%"
  )
  reg add "HKCU\Environment" /v Path /t REG_EXPAND_SZ /d "!NEW_PATH!" /f >nul
  echo     Added to PATH: %INSTALL_DIR%
) else (
  echo     Already in PATH, skipping.
)

echo.
echo  Neglish installed successfully!
echo  Location: %INSTALL_DIR%\neglish.exe
echo.
echo  Open a NEW terminal window and run:
echo    neglish --version
echo    neglish myprogram.neg
echo    neglish --repl
echo.
endlocal
