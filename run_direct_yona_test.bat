@echo off
REM Run the direct Yona communication test script

REM Set the OpenAI API key if not already set
if "%OPENAI_API_KEY%"=="" (
    if exist .env (
        for /f "tokens=*" %%a in (.env) do (
            set %%a
        )
    )
)

REM Set the Coral server URL if not already set
if "%CORAL_SERVER_URL%"=="" (
    set CORAL_SERVER_URL=http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse
)

REM Install required packages
pip install langchain>=0.1.0 langchain_mcp_adapters==0.0.11 langchain-openai>=0.0.2 aiohttp>=3.8.5

REM Run the test script
python test_direct_yona_communication.py %*
