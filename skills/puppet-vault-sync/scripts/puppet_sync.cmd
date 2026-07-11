@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
python3 "%SCRIPT_DIR%puppet_sync.py" %*
