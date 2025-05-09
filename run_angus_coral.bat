@echo off
REM Run Angus Coral Agent locally for testing

REM Set environment variables
set CORAL_SERVER_URL=https://coral.pushcollective.club/sse

REM Check if OpenAI API key is set
if "%OPENAI_API_KEY%"=="" (
    echo Warning: OPENAI_API_KEY environment variable is not set.
    echo The Coral Protocol integration may not work properly without it.
    echo Please set it using: set OPENAI_API_KEY=your-api-key
)

REM Install dependencies if needed
pip list | findstr "langchain_mcp_adapters" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing required dependencies...
    pip install -r requirements.coral.txt
)

REM Run the agent
echo Starting Angus Coral Agent...
python angus_coral_agent.py
