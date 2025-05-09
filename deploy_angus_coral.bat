@echo off
REM Deploy Angus Coral Agent on the server

REM Set variables
set SERVER=root@angs.club
set APP_DIR=/app

REM Display deployment information
echo Deploying Angus Coral Agent to %SERVER%:%APP_DIR%
echo This script will:
echo 1. Copy the necessary files to the server
echo 2. Update the docker-compose.yml file
echo 3. Restart the containers
echo.

REM Confirm deployment
set /p confirm=Do you want to continue? (y/n): 
if not "%confirm%"=="y" (
    echo Deployment cancelled.
    exit /b 0
)

REM Copy files to the server
echo Copying files to the server...
scp angus_coral_agent.py %SERVER%:%APP_DIR%/
if %ERRORLEVEL% NEQ 0 (
    echo Error copying files to the server.
    exit /b 1
)

scp Dockerfile.coral %SERVER%:%APP_DIR%/
if %ERRORLEVEL% NEQ 0 (
    echo Error copying files to the server.
    exit /b 1
)

scp requirements.coral.txt %SERVER%:%APP_DIR%/
if %ERRORLEVEL% NEQ 0 (
    echo Error copying files to the server.
    exit /b 1
)

scp docker-compose.yml %SERVER%:%APP_DIR%/
if %ERRORLEVEL% NEQ 0 (
    echo Error copying files to the server.
    exit /b 1
)

REM Restart containers
echo Restarting containers...
ssh %SERVER% "cd %APP_DIR% && docker-compose down && docker-compose up -d"
if %ERRORLEVEL% NEQ 0 (
    echo Error restarting containers.
    exit /b 1
)

REM Display logs
echo Displaying logs...
ssh %SERVER% "cd %APP_DIR% && docker-compose logs angus_coral | tail -n 20"

echo.
echo Deployment completed successfully.
echo You can check the logs using:
echo   ssh %SERVER% "cd %APP_DIR% && docker-compose logs -f angus_coral"
