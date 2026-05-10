@echo off
:: build_neglish_runtime.bat — Build neglish.exe and optionally install to PATH
:: Usage:
::   build_neglish_runtime.bat          ← build only
::   build_neglish_runtime.bat --install ← build and install to PATH

setlocal ENABLEDELAYEDEXPANSION

where py >nul 2>nul
if not errorlevel 1 (set "PY=py") else (
  where python >nul 2>nul
  if not errorlevel 1 (set "PY=python") else (
    echo [ERROR] Python not found. Install from python.org
    exit /b 1
  )
)

echo [1/3] Installing PyInstaller...
%PY% -m pip install --upgrade pyinstaller >nul
if errorlevel 1 (echo [ERROR] pip install failed & exit /b 1)

echo [2/3] Building neglish.exe (stdlib will be bundled inside)...
%PY% -m PyInstaller neglish.spec --clean --noconfirm
if errorlevel 1 (echo [ERROR] Build failed & exit /b 1)

echo [3/3] Done.
echo   Output: dist\neglish.exe
echo.

if /i "%~1"=="--install" (
  call install.bat dist\neglish.exe
) else (
  echo   To install to PATH, run:  install.bat
)
endlocal
