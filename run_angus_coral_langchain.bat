@echo off
REM Run Agent Angus with Coral Protocol LangChain integration
REM This script starts Agent Angus with the Coral Protocol LangChain integration,
REM allowing it to share its tools with other agents and use tools from other agents.

echo Starting Agent Angus with Coral Protocol LangChain integration...

REM Set default values
set SERVER_URL=http://coral.pushcollective.club/sse
set HOST=0.0.0.0
set PORT=5001
set DISCOVER=true

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :run
if /i "%~1"=="--server-url" (
    set SERVER_URL=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--host" (
    set HOST=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--no-discover" (
    set DISCOVER=false
    shift
    goto :parse_args
)
if /i "%~1"=="--help" (
    echo Usage: run_angus_coral_langchain.bat [options]
    echo.
    echo Options:
    echo   --server-url URL   URL of the Coral server (default: %SERVER_URL%)
    echo   --host HOST        Host to bind server to (default: %HOST%)
    echo   --port PORT        Port to bind server to (default: %PORT%)
    echo   --no-discover      Disable agent discovery on startup
    echo   --help             Show this help message
    exit /b 0
)
shift
goto :parse_args

:run
echo Server URL: %SERVER_URL%
echo Host: %HOST%
echo Port: %PORT%
echo Discover: %DISCOVER%

REM Build the command
set CMD=python run_angus_coral_langchain.py --server-url "%SERVER_URL%" --host "%HOST%" --port %PORT%
if "%DISCOVER%"=="false" set CMD=%CMD% --no-discover

echo Running command: %CMD%
echo.

REM Run the command
%CMD%

echo.
if %ERRORLEVEL% EQU 0 (
    echo Agent Angus with Coral Protocol LangChain integration stopped successfully.
) else (
    echo Agent Angus with Coral Protocol LangChain integration failed with error code %ERRORLEVEL%.
)
