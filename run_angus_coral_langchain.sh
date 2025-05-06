#!/bin/bash
# Run Agent Angus with Coral Protocol LangChain integration
# This script starts Agent Angus with the Coral Protocol LangChain integration,
# allowing it to share its tools with other agents and use tools from other agents.

echo "Starting Agent Angus with Coral Protocol LangChain integration..."

# Set default values
SERVER_URL="http://coral.pushcollective.club/sse"
HOST="0.0.0.0"
PORT=5001
DISCOVER=true

# Function to show help
show_help() {
    echo "Usage: run_angus_coral_langchain.sh [options]"
    echo ""
    echo "Options:"
    echo "  --server-url URL   URL of the Coral server (default: $SERVER_URL)"
    echo "  --host HOST        Host to bind server to (default: $HOST)"
    echo "  --port PORT        Port to bind server to (default: $PORT)"
    echo "  --no-discover      Disable agent discovery on startup"
    echo "  --help             Show this help message"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --server-url)
            SERVER_URL="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --no-discover)
            DISCOVER=false
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

echo "Server URL: $SERVER_URL"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Discover: $DISCOVER"

# Build the command
CMD="python run_angus_coral_langchain.py --server-url \"$SERVER_URL\" --host \"$HOST\" --port $PORT"
if [ "$DISCOVER" = "false" ]; then
    CMD="$CMD --no-discover"
fi

echo "Running command: $CMD"
echo ""

# Run the command
eval $CMD
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "Agent Angus with Coral Protocol LangChain integration stopped successfully."
else
    echo "Agent Angus with Coral Protocol LangChain integration failed with error code $EXIT_CODE."
fi

exit $EXIT_CODE
