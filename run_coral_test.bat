@echo off
REM Run Angus Coral Agent test script

REM Set environment variables
set CORAL_SERVER_URL=https://coral.pushcollective.club/sse

REM Check if requests library is installed
pip list | findstr "requests" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing required dependencies...
    pip install requests
)

REM Run the test script
echo Running Angus Coral Agent test script...
python test_angus_coral.py

echo.
echo If the test shows that the Angus agent is not registered,
echo make sure the Angus Coral Agent is running using run_angus_coral.bat
