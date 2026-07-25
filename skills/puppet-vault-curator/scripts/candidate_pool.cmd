@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
python3 "%SCRIPT_DIR%candidate_pool.py" %*
exit /b %ERRORLEVEL%
