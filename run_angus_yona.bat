@echo off
REM Run the Angus-Yona communication script

REM Set default values
if "%CORAL_SERVER_URL%"=="" (
    set SERVER_URL=http://coral.pushcollective.club:5555
) else (
    set SERVER_URL=%CORAL_SERVER_URL%
)
set AGENT_ID=angus_agent
set TARGET_AGENT_ID=yona
set SESSION_ID=session1
set PROMPT=Create a happy K-pop song about friendship between AI agents
set TIMEOUT=300
set WAIT_FOR_AGENTS=2

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :run_script
if "%~1"=="--server-url" (
    set SERVER_URL=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--agent-id" (
    set AGENT_ID=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--target-agent-id" (
    set TARGET_AGENT_ID=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--session-id" (
    set SESSION_ID=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--prompt" (
    set PROMPT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--timeout" (
    set TIMEOUT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--wait-for-agents" (
    set WAIT_FOR_AGENTS=%~2
    shift
    shift
    goto :parse_args
)
echo Unknown option: %~1
exit /b 1

:run_script
REM Run the script
python angus_yona_communication.py ^
    --server-url "%SERVER_URL%" ^
    --agent-id "%AGENT_ID%" ^
    --target-agent-id "%TARGET_AGENT_ID%" ^
    --session-id "%SESSION_ID%" ^
    --prompt "%PROMPT%" ^
    --timeout "%TIMEOUT%" ^
    --wait-for-agents "%WAIT_FOR_AGENTS%"
