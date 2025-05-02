@echo off
REM Run script for Agent Angus with Coral Protocol integration (Windows)

echo Starting Agent Angus with Coral Protocol integration...

REM Set environment variables for Coral integration
set CORAL_SERVER_URL=http://coral.pushcollective.club:3001
set AGENT_ID=did:web:angus.ai

REM Run the Python script
python run_angus_coral.py %*

echo Agent Angus with Coral Protocol integration has been stopped.
