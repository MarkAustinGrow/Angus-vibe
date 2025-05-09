#!/bin/bash
# Run the Coral Protocol discovery test with dynamic session ID handling

# Set environment variables
export PYTHONPATH=.
export CORAL_SERVER_URL=${CORAL_SERVER_URL:-"http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse"}

# Default container name
CONTAINER_NAME="app_angus_coral_1"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --container-name)
      CONTAINER_NAME="$2"
      shift 2
      ;;
    --server-url)
      export CORAL_SERVER_URL="$2"
      shift 2
      ;;
    --session-id)
      export CORAL_SESSION_ID="$2"
      shift 2
      ;;
    *)
      # Pass other arguments to the discovery script
      ARGS="$ARGS $1"
      shift
      ;;
  esac
done

# Extract session ID from Docker logs if not provided
if [ -z "$CORAL_SESSION_ID" ]; then
  echo "Extracting session ID from Docker logs..."
  SESSION_ID=$(docker logs $CONTAINER_NAME 2>/dev/null | grep -o "Extracted session ID: [0-9a-f-]\+" | tail -1 | cut -d' ' -f4)
  
  if [ -n "$SESSION_ID" ]; then
    echo "Found session ID: $SESSION_ID"
    export CORAL_SESSION_ID="$SESSION_ID"
  else
    echo "Could not extract session ID from Docker logs"
  fi
fi

# Run the discovery script
if [ -n "$CORAL_SESSION_ID" ]; then
  echo "Running discovery script with session ID: $CORAL_SESSION_ID"
  python3 docker_test_discovery.py --container-name "$CONTAINER_NAME" $ARGS
else
  echo "Running discovery script without session ID"
  python3 docker_test_discovery.py --container-name "$CONTAINER_NAME" $ARGS
fi
