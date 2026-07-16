@echo off
rem =====================================================================
rem  상권별 엑셀 분리 실행파일
rem  - C열(상권구분) 값에 따라 엑셀 파일을 각각 생성합니다.
rem  - 사용법 1) 이 파일을 더블클릭 (같은 폴더의 .xlsx 자동 인식)
rem  - 사용법 2) 원본 엑셀 파일을 이 파일 위로 끌어다 놓기(드래그 앤 드롭)
rem =====================================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PS1=%~dp0split_by_district.ps1"

if not exist "%PS1%" (
    echo [오류] split_by_district.ps1 파일을 찾을 수 없습니다.
    echo        이 배치 파일과 같은 폴더에 있어야 합니다.
    echo.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%" %1

echo.
pause
endlocal
