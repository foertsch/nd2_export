@echo off
setlocal

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if not exist ".venv\Scripts\pythonw.exe" (
  echo The local Python environment is missing.
  echo Run install_windows_python.bat first.
  pause
  exit /b 1
)

set PYTHONPATH=%SCRIPT_DIR%src
".venv\Scripts\pythonw.exe" "launch_nd2_export_gui.pyw"
