@echo off
setlocal
chcp 65001 >nul
set "SCRIPT_DIR=%~dp0"
python3 "%SCRIPT_DIR%install_agent_entries.py" %*
exit /b %ERRORLEVEL%
