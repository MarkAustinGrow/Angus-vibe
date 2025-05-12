@echo off
REM Deploy the improved Yona integration to a server

REM Set default values
set SERVER_USER=root
set SERVER_HOST=angs.club
set SERVER_DIR=/opt/Angus-vibe
set BRANCH=working-version

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse_args
if "%~1"=="--user" (
    set SERVER_USER=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--host" (
    set SERVER_HOST=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--dir" (
    set SERVER_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--branch" (
    set BRANCH=%~2
    shift
    shift
    goto :parse_args
)
echo Unknown option: %~1
exit /b 1
:end_parse_args

echo Deploying improved Yona integration to %SERVER_USER%@%SERVER_HOST%:%SERVER_DIR%

REM Create a temporary directory for the files
set TEMP_DIR=%TEMP%\improved_yona_integration_%RANDOM%
mkdir %TEMP_DIR%
echo Created temporary directory: %TEMP_DIR%

REM Copy the files to the temporary directory
echo Copying files to temporary directory...
copy src\coral_protocol\langchain\runnable.py %TEMP_DIR%\
copy angus_coral_adapter.py %TEMP_DIR%\
copy test_improved_yona_communication.py %TEMP_DIR%\
copy run_improved_yona_test.sh %TEMP_DIR%\
copy run_improved_yona_test.bat %TEMP_DIR%\
copy IMPROVED_YONA_INTEGRATION.md %TEMP_DIR%\

REM Create the deployment script
echo #!/bin/bash > %TEMP_DIR%\deploy.sh
echo # Deploy the improved Yona integration >> %TEMP_DIR%\deploy.sh
echo. >> %TEMP_DIR%\deploy.sh
echo # Set the directory >> %TEMP_DIR%\deploy.sh
echo SERVER_DIR="%SERVER_DIR%" >> %TEMP_DIR%\deploy.sh
echo cd $SERVER_DIR >> %TEMP_DIR%\deploy.sh
echo. >> %TEMP_DIR%\deploy.sh
echo # Create the directory structure if it doesn't exist >> %TEMP_DIR%\deploy.sh
echo mkdir -p src/coral_protocol/langchain >> %TEMP_DIR%\deploy.sh
echo. >> %TEMP_DIR%\deploy.sh
echo # Copy the files >> %TEMP_DIR%\deploy.sh
echo cp runnable.py src/coral_protocol/langchain/ >> %TEMP_DIR%\deploy.sh
echo cp angus_coral_adapter.py ./ >> %TEMP_DIR%\deploy.sh
echo cp test_improved_yona_communication.py ./ >> %TEMP_DIR%\deploy.sh
echo cp run_improved_yona_test.sh ./ >> %TEMP_DIR%\deploy.sh
echo cp run_improved_yona_test.bat ./ >> %TEMP_DIR%\deploy.sh
echo cp IMPROVED_YONA_INTEGRATION.md ./ >> %TEMP_DIR%\deploy.sh
echo. >> %TEMP_DIR%\deploy.sh
echo # Make the scripts executable >> %TEMP_DIR%\deploy.sh
echo chmod +x run_improved_yona_test.sh >> %TEMP_DIR%\deploy.sh
echo. >> %TEMP_DIR%\deploy.sh
echo # Restart the Docker containers >> %TEMP_DIR%\deploy.sh
echo docker-compose down >> %TEMP_DIR%\deploy.sh
echo docker-compose build angus_coral >> %TEMP_DIR%\deploy.sh
echo docker-compose up -d >> %TEMP_DIR%\deploy.sh
echo. >> %TEMP_DIR%\deploy.sh
echo echo "Deployment completed successfully!" >> %TEMP_DIR%\deploy.sh

REM Copy the files to the server using pscp (PuTTY SCP)
echo Copying files to the server...
where pscp >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: pscp not found. Please install PuTTY and add it to your PATH.
    exit /b 1
)
pscp -r %TEMP_DIR%\* %SERVER_USER%@%SERVER_HOST%:/tmp/

REM Execute the deployment script on the server using plink (PuTTY Link)
echo Executing deployment script on the server...
where plink >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: plink not found. Please install PuTTY and add it to your PATH.
    exit /b 1
)
plink %SERVER_USER%@%SERVER_HOST% "bash /tmp/deploy.sh"

REM Clean up the temporary directory
echo Cleaning up temporary directory...
rmdir /s /q %TEMP_DIR%

echo Deployment completed successfully!
