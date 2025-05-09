@echo off
REM Run the Coral Protocol discovery test with dynamic session ID handling

REM Set environment variables
set PYTHONPATH=.
if not defined CORAL_SERVER_URL set CORAL_SERVER_URL=http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse

REM Default container name
set CONTAINER_NAME=app_angus_coral_1

REM Parse command line arguments
set ARGS=

:parse_args
if "%~1"=="" goto :end_parse_args
if "%~1"=="--container-name" (
    set CONTAINER_NAME=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--server-url" (
    set CORAL_SERVER_URL=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--session-id" (
    set CORAL_SESSION_ID=%~2
    shift
    shift
    goto :parse_args
)
set ARGS=%ARGS% %~1
shift
goto :parse_args

:end_parse_args

REM Extract session ID from Docker logs if not provided
if not defined CORAL_SESSION_ID (
    echo Extracting session ID from Docker logs...
    for /f "tokens=4" %%i in ('docker logs %CONTAINER_NAME% 2^>nul ^| findstr /C:"Extracted session ID:"') do (
        set SESSION_ID=%%i
    )
    
    if defined SESSION_ID (
        echo Found session ID: %SESSION_ID%
        set CORAL_SESSION_ID=%SESSION_ID%
    ) else (
        echo Could not extract session ID from Docker logs
    )
)

REM Run the discovery script
if defined CORAL_SESSION_ID (
    echo Running discovery script with session ID: %CORAL_SESSION_ID%
    python docker_test_discovery.py --container-name "%CONTAINER_NAME%" %ARGS%
) else (
    echo Running discovery script without session ID
    python docker_test_discovery.py --container-name "%CONTAINER_NAME%" %ARGS%
)
