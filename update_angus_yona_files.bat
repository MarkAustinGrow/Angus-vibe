@echo off
REM Script to update Angus-Yona integration files on the server

echo ========================================
echo   Updating Angus-Yona Integration Files 
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

REM Copy the updated files
echo Copying updated files...

REM Copy the main adapter file
copy angus_coral_adapter.py "%TARGET_DIR%\"
echo Copied angus_coral_adapter.py

REM Copy the test files
copy test_angus_yona_communication.py "%TARGET_DIR%\"
echo Copied test_angus_yona_communication.py

copy run_angus_yona_test.bat "%TARGET_DIR%\"
echo Copied run_angus_yona_test.bat

REM Copy the documentation
copy ANGUS_YONA_INTEGRATION.md "%TARGET_DIR%\"
echo Copied ANGUS_YONA_INTEGRATION.md

echo All files copied successfully.

REM Ask if the user wants to restart the Coral adapter
set /p RESTART="Do you want to restart the Coral adapter? (y/n): "

if /i "%RESTART%"=="y" (
    echo Restarting Coral adapter...
    cd /d "%TARGET_DIR%"
    docker-compose restart coral
    
    REM Check if the restart was successful
    if %ERRORLEVEL% EQU 0 (
        echo Coral adapter restarted successfully.
        echo Displaying logs...
        docker logs angus_coral_1
    ) else (
        echo Error: Failed to restart Coral adapter.
        echo Please check the Docker logs for more information.
    )
) else (
    echo Skipping restart. You can restart the Coral adapter manually with:
    echo cd /d %TARGET_DIR% ^&^& docker-compose restart coral
)

echo ========================================
echo   Update completed!                     
echo ========================================

pause
