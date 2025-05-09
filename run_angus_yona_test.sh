#!/bin/bash
# Run the Angus-Yona communication test

# Set environment variables
export PYTHONPATH=.
export CORAL_SERVER_URL=${CORAL_SERVER_URL:-"http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse"}

# Run the test script
python test_angus_yona_communication.py "$@"
