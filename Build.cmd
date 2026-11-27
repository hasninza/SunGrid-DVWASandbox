@echo off
setlocal
set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%host\build.py" %*
if errorlevel 1 (
  echo.
  echo Build failed. Review the messages above.
  exit /b 1
)
