@echo off
REM Run the agent-based Yona communication script

REM Set default values
if "%CORAL_SERVER_URL%"=="" (
    set SERVER_URL=http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse
) else (
    set SERVER_URL=%CORAL_SERVER_URL%
)
set AGENT_ID=angus_agent
set AGENT_DESCRIPTION=Angus is a music analysis agent that can analyze songs and provide feedback
set YONA_ID=yona
set PROMPT=Create a happy K-pop song about friendship between AI agents
set TIMEOUT=300
set WAIT_FOR_AGENTS=2
set MODEL=gpt-4o-mini

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :check_api_key
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
if "%~1"=="--agent-description" (
    set AGENT_DESCRIPTION=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--yona-id" (
    set YONA_ID=%~2
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
if "%~1"=="--model" (
    set MODEL=%~2
    shift
    shift
    goto :parse_args
)
echo Unknown option: %~1
exit /b 1

:check_api_key
REM Check if OPENAI_API_KEY is set
if "%OPENAI_API_KEY%"=="" (
    echo Error: OPENAI_API_KEY environment variable is not set.
    echo Please set it using: set OPENAI_API_KEY=your_api_key
    exit /b 1
)

REM Run the script
python agent_yona_communication.py ^
    --server-url "%SERVER_URL%" ^
    --agent-id "%AGENT_ID%" ^
    --agent-description "%AGENT_DESCRIPTION%" ^
    --yona-id "%YONA_ID%" ^
    --prompt "%PROMPT%" ^
    --timeout "%TIMEOUT%" ^
    --wait-for-agents "%WAIT_FOR_AGENTS%" ^
    --model "%MODEL%"
