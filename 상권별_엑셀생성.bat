@echo off
rem =====================================================================
rem  Split Excel by district (C column)
rem  - Double-click this file, or drag an .xlsx file onto it.
rem  - Do NOT put Korean text in this .bat file (encoding safety).
rem =====================================================================
setlocal
cd /d "%~dp0"

set "PS1=%~dp0split_by_district.ps1"

if not exist "%PS1%" (
    echo [ERROR] split_by_district.ps1 was not found in this folder.
    echo         Keep this .bat and split_by_district.ps1 in the SAME folder.
    echo.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %1

echo.
pause
endlocal
