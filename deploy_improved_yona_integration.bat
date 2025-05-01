@echo off
REM Deployment script for the improved Angus-Yona integration

echo ========================================
echo   Deploying Improved Yona Integration   
echo ========================================

REM Check if the target directory is provided
if "%~1"=="" (
    set TARGET_DIR=C:\opt\angus
    echo No target directory provided, using default: %TARGET_DIR%
) else (
    set TARGET_DIR=%~1
    echo Target directory: %TARGET_DIR%
)

REM Check if the target directory exists
if not exist "%TARGET_DIR%" (
    echo Error: Target directory does not exist: %TARGET_DIR%
    exit /b 1
)

REM Copy the improved files
echo Copying improved files...

REM Copy the main adapter file
copy angus_coral_adapter_improved.py "%TARGET_DIR%\"
echo Copied angus_coral_adapter_improved.py

REM Copy the test files
copy test_improved_yona_communication.py "%TARGET_DIR%\"
echo Copied test_improved_yona_communication.py

copy run_improved_yona_test.bat "%TARGET_DIR%\"
echo Copied run_improved_yona_test.bat

REM Copy the documentation
copy IMPROVED_YONA_INTEGRATION.md "%TARGET_DIR%\"
echo Copied IMPROVED_YONA_INTEGRATION.md

echo All improved files copied successfully.

REM Ask if the user wants to restart the Coral adapter
set /p RESTART="Do you want to restart the Coral adapter with the improved version? (y/n): "

if /i "%RESTART%"=="y" (
    echo Updating the Docker configuration to use the improved adapter...
    
    REM Create a backup of the original Dockerfile
    copy "%TARGET_DIR%\Dockerfile" "%TARGET_DIR%\Dockerfile.backup"
    echo Created backup of original Dockerfile: Dockerfile.backup
    
    REM Update the Dockerfile to use the improved adapter
    powershell -Command "(Get-Content '%TARGET_DIR%\Dockerfile') -replace 'CMD \[""python"", ""angus_coral_adapter.py""\]', 'CMD [""python"", ""angus_coral_adapter_improved.py""]' | Set-Content '%TARGET_DIR%\Dockerfile'"
    echo Updated Dockerfile to use the improved adapter
    
    REM Rebuild and restart the Docker containers
    echo Rebuilding Docker images...
    cd /d "%TARGET_DIR%"
    docker-compose build
    
    REM Check if the build was successful
    if %ERRORLEVEL% EQU 0 (
        echo Restarting Docker containers...
        docker-compose down
        docker-compose up -d
        
        REM Check if the containers are running
        echo Checking container status...
        docker ps
        
        REM Display the logs of the Coral Protocol adapter
        echo Displaying logs of the Coral Protocol adapter...
        docker logs angus_coral_1
        
        echo ========================================
        echo   Deployment completed successfully!    
        echo ========================================
        echo The improved Angus-Yona integration is now running.
        echo You can check the logs with: docker logs angus_coral_1
    ) else (
        echo Error: Failed to build Docker images.
        echo Restoring original Dockerfile...
        copy "%TARGET_DIR%\Dockerfile.backup" "%TARGET_DIR%\Dockerfile"
        echo Please check the build logs for more information.
        exit /b 1
    )
) else (
    echo Skipping restart. You can manually update the Docker configuration and restart the containers with:
    echo 1. Edit %TARGET_DIR%\Dockerfile to use angus_coral_adapter_improved.py
    echo 2. cd /d %TARGET_DIR% ^&^& docker-compose build
    echo 3. docker-compose down ^&^& docker-compose up -d
)

echo ========================================
echo   Deployment script completed!          
echo ========================================

pause
