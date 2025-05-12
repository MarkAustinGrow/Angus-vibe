#!/bin/bash
# Run the improved Yona communication test script

# Set the OpenAI API key if not already set
if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f .env ]; then
        source .env
    fi
fi

# Set the Coral server URL if not already set
if [ -z "$CORAL_SERVER_URL" ]; then
    export CORAL_SERVER_URL="http://coral.pushcollective.club:3001/devmode/default-app/default-key/session1/sse"
fi

# Run the test script
python3 test_improved_yona_communication.py "$@"
