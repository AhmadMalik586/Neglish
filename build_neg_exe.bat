@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Build standalone EXE from a .neg file (no Python required at runtime).
REM Usage:
REM   build_neg_exe.bat your_program.neg
REM   build_neg_exe.bat your_program.neg myapp

if "%~1"=="" (
  echo Usage: build_neg_exe.bat ^<file.neg^> [output_name]
  exit /b 1
)

set "NEG_FILE=%~1"
set "OUT_NAME=%~2"

if not exist "%NEG_FILE%" (
  echo [ERROR] File not found: %NEG_FILE%
  exit /b 1
)

if "%OUT_NAME%"=="" set "OUT_NAME=%~n1"

where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo [ERROR] Python is required for building.
    exit /b 1
  )
  set "PY=python"
) else (
  set "PY=py"
)

echo [1/3] Installing build dependencies...
%PY% -m pip install --upgrade pyinstaller >nul
if errorlevel 1 (
  echo [ERROR] Failed to install PyInstaller.
  exit /b 1
)

set "ICON_ARG="
if exist "negextension.ico" set "ICON_ARG=--icon negextension.ico"

echo [2/3] Building %NEG_FILE% into %OUT_NAME%.exe ...
%PY% "tools\neg_to_exe.py" "%NEG_FILE%" -o "%OUT_NAME%" %ICON_ARG%
if errorlevel 1 (
  echo [ERROR] Build failed.
  exit /b 1
)

echo [3/3] Done.
echo Output: dist\%OUT_NAME%.exe
echo Tip: You can run it on machines without Python installed.
exit /b 0
