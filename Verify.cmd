@echo off
setlocal
set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%verify.py" %*
exit /b %errorlevel%
