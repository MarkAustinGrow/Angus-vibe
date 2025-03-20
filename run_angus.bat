@echo off
REM Batch script to run Agent Angus with common commands

REM Function to display help
:show_help
echo Agent Angus - YouTube Publishing and Feedback Collection
echo.
echo Usage: run_angus.bat [command] [options]
echo.
echo Commands:
echo   setup       Create the YouTube table in Supabase
echo   upload      Upload pending songs to YouTube
echo   comments    Fetch comments for uploaded videos
echo   daemon      Run in daemon mode with scheduled tasks
echo   test        Run tests in simulation mode
echo   help        Show this help message
echo.
echo Options:
echo   --limit N   Limit the number of items to process (default: 10)
echo   --simulate  Run in simulation mode without making actual API calls
echo.
echo Examples:
echo   run_angus.bat setup
echo   run_angus.bat upload --limit 5
echo   run_angus.bat comments --limit 10
echo   run_angus.bat upload --simulate
echo   run_angus.bat test
goto :eof

REM Default values
set LIMIT=10
set SIMULATE=

REM Parse command
set COMMAND=%1
shift

REM Parse options
:parse_args
if "%1"=="" goto execute_command
if "%1"=="--limit" (
    set LIMIT=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--simulate" (
    set SIMULATE=--simulate
    shift
    goto parse_args
)
echo Unknown option: %1
call :show_help
exit /b 1

REM Execute command
:execute_command
if "%COMMAND%"=="setup" (
    echo Creating YouTube table in Supabase...
    python angus.py --create-table %SIMULATE%
    goto :eof
)
if "%COMMAND%"=="upload" (
    echo Uploading songs to YouTube (limit: %LIMIT%)...
    python angus.py --upload --limit %LIMIT% %SIMULATE%
    goto :eof
)
if "%COMMAND%"=="comments" (
    echo Fetching comments for uploaded videos (limit: %LIMIT%)...
    python angus.py --fetch-comments --limit %LIMIT% %SIMULATE%
    goto :eof
)
if "%COMMAND%"=="daemon" (
    echo Starting Agent Angus in daemon mode...
    python angus.py --daemon
    goto :eof
)
if "%COMMAND%"=="test" (
    echo Running tests in simulation mode...
    python test_angus.py
    goto :eof
)
if "%COMMAND%"=="help" (
    call :show_help
    goto :eof
)
echo Unknown command: %COMMAND%
call :show_help
exit /b 1
