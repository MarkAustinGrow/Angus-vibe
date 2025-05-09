#!/bin/bash
# Run the Coral Protocol discovery test from inside the Docker container

# Set environment variables
export PYTHONPATH=.
export CORAL_SERVER_URL=${CORAL_SERVER_URL:-"http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse"}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --server-url)
      export CORAL_SERVER_URL="$2"
      shift 2
      ;;
    --session-id)
      export CORAL_SESSION_ID="$2"
      shift 2
      ;;
    --log-file)
      LOG_FILE="$2"
      shift 2
      ;;
    *)
      # Pass other arguments to the discovery script
      ARGS="$ARGS $1"
      shift
      ;;
  esac
done

# Default log file
LOG_FILE=${LOG_FILE:-"/var/log/app.log"}

# Extract session ID from container logs if not provided
if [ -z "$CORAL_SESSION_ID" ]; then
  echo "Extracting session ID from container logs..."
  
  # Try to extract from process output
  SESSION_ID=$(grep -r "Extracted session ID" /proc/*/fd/ 2>/dev/null | grep -o "Extracted session ID: [0-9a-f-]\+" | tail -1 | cut -d' ' -f4)
  
  if [ -n "$SESSION_ID" ]; then
    echo "Found session ID from process output: $SESSION_ID"
    export CORAL_SESSION_ID="$SESSION_ID"
  else
    # Try to extract from log file
    if [ -f "$LOG_FILE" ]; then
      SESSION_ID=$(grep -o "Extracted session ID: [0-9a-f-]\+" "$LOG_FILE" 2>/dev/null | tail -1 | cut -d' ' -f4)
      
      if [ -n "$SESSION_ID" ]; then
        echo "Found session ID from log file: $SESSION_ID"
        export CORAL_SESSION_ID="$SESSION_ID"
      else
        echo "Could not extract session ID from log file"
      fi
    else
      echo "Log file not found: $LOG_FILE"
    fi
  fi
  
  # If still not found, try to extract from stdout/stderr
  if [ -z "$CORAL_SESSION_ID" ]; then
    SESSION_ID=$(grep -o "Extracted session ID: [0-9a-f-]\+" /dev/stdout /dev/stderr 2>/dev/null | tail -1 | cut -d' ' -f4)
    
    if [ -n "$SESSION_ID" ]; then
      echo "Found session ID from stdout/stderr: $SESSION_ID"
      export CORAL_SESSION_ID="$SESSION_ID"
    else
      echo "Could not extract session ID from stdout/stderr"
    fi
  fi
fi

# Run the discovery script
if [ -n "$CORAL_SESSION_ID" ]; then
  echo "Running discovery script with session ID: $CORAL_SESSION_ID"
  python3 docker_test_discovery.py --log-file "$LOG_FILE" $ARGS
else
  echo "Running discovery script without session ID"
  python3 docker_test_discovery.py --log-file "$LOG_FILE" $ARGS
fi
