@echo off
REM Run scheduled operations for Agent Angus with CrewAI integration
REM This batch file runs the scheduled operations for Agent Angus with CrewAI integration

echo Starting scheduled operations for Agent Angus with CrewAI integration...

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in the PATH.
    echo Please install Python and try again.
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment.
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo Failed to activate virtual environment.
    exit /b 1
)

REM Install dependencies if needed
if not exist venv\Lib\site-packages\crewai (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Failed to install dependencies.
        exit /b 1
    )
)

REM Check for --simple-tools flag
set USE_SIMPLE_TOOLS=
for %%a in (%*) do (
    if "%%a"=="--simple-tools" (
        set USE_SIMPLE_TOOLS=--simple-tools
        echo Using simple tools created with the @tool decorator
    )
)

REM Run the scheduled operations
echo Running scheduled operations for Agent Angus with CrewAI integration...
python scheduled_crew.py %* %USE_SIMPLE_TOOLS%

REM Note: We don't deactivate the virtual environment because the scheduled operations
REM run continuously. The script will only exit when the user presses Ctrl+C.
