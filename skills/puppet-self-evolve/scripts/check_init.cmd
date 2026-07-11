@echo off
setlocal EnableExtensions

rem Wrapper for check_init.py with Python 3 resolution.
rem Usage:
rem   check_init.cmd --workspace "E:\your-workspace"
rem   check_init.cmd --agents-home "%USERPROFILE%\.codex"
rem   check_init.cmd --cursor-home "%USERPROFILE%\.cursor"
rem   check_init.cmd --help

set "SCRIPT_DIR=%~dp0"
set "PY_SCRIPT=%SCRIPT_DIR%check_init.py"

if not exist "%PY_SCRIPT%" (
  echo [ERROR] Python helper script not found: "%PY_SCRIPT%"
  exit /b 1
)

set "RESOLVE_PY=%~dp0..\..\..\..\sc-core\scripts\resolve_python.cmd"
if not exist "%RESOLVE_PY%" set "RESOLVE_PY=%~dp0..\..\..\scripts\resolve_python.cmd"
if not exist "%RESOLVE_PY%" (
  echo [ERROR] resolve_python.cmd not found: "%RESOLVE_PY%"
  exit /b 1
)

call "%RESOLVE_PY%"
if errorlevel 1 exit /b 1

if "%SKILLS_PY_ARGS%"=="" (
  "%SKILLS_PY_CMD%" "%PY_SCRIPT%" %*
) else (
  "%SKILLS_PY_CMD%" %SKILLS_PY_ARGS% "%PY_SCRIPT%" %*
)
exit /b %ERRORLEVEL%
