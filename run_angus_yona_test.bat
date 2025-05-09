@echo off
REM Run the Angus-Yona communication test

REM Set environment variables
set PYTHONPATH=.
if not defined CORAL_SERVER_URL set CORAL_SERVER_URL=http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse

REM Run the test script
python test_angus_yona_communication.py %*
