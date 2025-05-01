@echo off
echo Starting Improved Angus-Yona communication test...

REM Parse command line arguments
set MESSAGE=
set TIMEOUT=300
set VERIFY=true

:parse_args
if "%~1"=="" goto run_test
if /i "%~1"=="--message" (
    set MESSAGE=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--timeout" (
    set TIMEOUT=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--no-verify" (
    set VERIFY=false
    shift
    goto parse_args
)
shift
goto parse_args

:run_test
echo Parameters:
if not "%MESSAGE%"=="" echo Message: %MESSAGE%
echo Timeout: %TIMEOUT% seconds
echo Verify delivery: %VERIFY%
echo.

REM Build the command
set CMD=python test_improved_yona_communication.py
if not "%MESSAGE%"=="" set CMD=%CMD% --message "%MESSAGE%"
if not "%TIMEOUT%"=="300" set CMD=%CMD% --timeout %TIMEOUT%
if "%VERIFY%"=="false" set CMD=%CMD% --no-verify

echo Running: %CMD%
echo.
%CMD%

echo.
echo Test completed.
pause
