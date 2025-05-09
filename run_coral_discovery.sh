#!/bin/bash
# Run the Coral Protocol discovery test

# Set environment variables
export PYTHONPATH=.
export CORAL_SERVER_URL=${CORAL_SERVER_URL:-"http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse"}

# Extract session ID from logs if available
SESSION_ID=$(grep -o "Extracted session ID: [0-9a-f-]\+" /var/log/app_angus_coral_1.log 2>/dev/null | tail -1 | cut -d' ' -f4)

if [ -n "$SESSION_ID" ]; then
  echo "Using session ID from logs: $SESSION_ID"
  python3 test_coral_discovery.py --session-id "$SESSION_ID" "$@"
else
  echo "No session ID found in logs, proceeding without it"
  python3 test_coral_discovery.py "$@"
fi
