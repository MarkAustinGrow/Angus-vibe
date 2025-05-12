@echo off
REM Run the MCP discovery script

REM Set default values
if "%CORAL_SERVER_URL%"=="" (
    set SERVER_URL=http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse
) else (
    set SERVER_URL=%CORAL_SERVER_URL%
)
set AGENT_ID=discovery_agent
set AGENT_DESCRIPTION=Agent for discovering other agents
set WAIT_FOR_AGENTS=2
set TIMEOUT=300
set YONA_ID=yona

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
if "%~1"=="--agent-description" (
    set AGENT_DESCRIPTION=%~2
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
if "%~1"=="--timeout" (
    set TIMEOUT=%~2
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
echo Unknown option: %~1
exit /b 1

:run_script
REM Run the script
python mcp_discovery.py ^
    --server-url "%SERVER_URL%" ^
    --agent-id "%AGENT_ID%" ^
    --agent-description "%AGENT_DESCRIPTION%" ^
    --wait-for-agents "%WAIT_FOR_AGENTS%" ^
    --timeout "%TIMEOUT%" ^
    --yona-id "%YONA_ID%"
