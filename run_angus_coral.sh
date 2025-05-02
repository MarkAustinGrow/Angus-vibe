#!/bin/bash
# Run script for Agent Angus with Coral Protocol integration (Unix/Linux/macOS)

echo "Starting Agent Angus with Coral Protocol integration..."

# Set environment variables for Coral integration
export CORAL_SERVER_URL="http://coral.pushcollective.club:3001"
export AGENT_ID="did:web:angus.ai"

# Run the Python script
python3 run_angus_coral.py "$@"

echo "Agent Angus with Coral Protocol integration has been stopped."
