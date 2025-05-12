@echo off
REM Run the improved Yona communication test script

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

REM Run the test script
python test_improved_yona_communication.py %*
