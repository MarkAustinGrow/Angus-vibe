#!/bin/bash
# Run the direct Yona communication test script

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

# Install required packages
pip install langchain>=0.1.0 langchain_mcp_adapters==0.0.11 langchain-openai>=0.0.2 aiohttp>=3.8.5

# Run the test script
python3 test_direct_yona_communication.py "$@"
