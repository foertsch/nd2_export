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

echo Creating virtual environment...
py -3 -m venv .venv
if errorlevel 1 (
  echo Failed to create virtual environment.
  pause
  exit /b 1
)

echo Installing project and dependencies...
call ".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
  echo Failed to upgrade pip.
  pause
  exit /b 1
)

call ".venv\Scripts\python.exe" -m pip install .
if errorlevel 1 (
  echo Failed to install the ND2 exporter.
  pause
  exit /b 1
)

echo.
echo Installation finished.
echo You can now double-click launch_nd2_export_gui.bat
pause
