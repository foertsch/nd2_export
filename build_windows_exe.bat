@echo off
setlocal

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher not found.
  echo Please install Python 3.9 or newer from https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3 -m venv .venv
)

echo Installing build dependencies...
call ".venv\Scripts\python.exe" -m pip install --upgrade pip
call ".venv\Scripts\python.exe" -m pip install .[dev]
if errorlevel 1 (
  echo Failed to install build dependencies.
  pause
  exit /b 1
)

echo Building Windows executable...
call ".venv\Scripts\pyinstaller.exe" nd2_export_gui.spec --noconfirm
if errorlevel 1 (
  echo PyInstaller build failed.
  pause
  exit /b 1
)

echo.
echo Build complete. Check the dist folder.
pause
