#!/bin/bash
# Run the Angus-Yona communication script

# Set default values
SERVER_URL=${CORAL_SERVER_URL:-"http://coral.pushcollective.club:5555"}
AGENT_ID="angus_agent"
TARGET_AGENT_ID="yona"
SESSION_ID="session1"
PROMPT="Create a happy K-pop song about friendship between AI agents"
TIMEOUT=300
WAIT_FOR_AGENTS=2

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --server-url)
            SERVER_URL="$2"
            shift 2
            ;;
        --agent-id)
            AGENT_ID="$2"
            shift 2
            ;;
        --target-agent-id)
            TARGET_AGENT_ID="$2"
            shift 2
            ;;
        --session-id)
            SESSION_ID="$2"
            shift 2
            ;;
        --prompt)
            PROMPT="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --wait-for-agents)
            WAIT_FOR_AGENTS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run the script
python3 angus_yona_communication.py \
    --server-url "$SERVER_URL" \
    --agent-id "$AGENT_ID" \
    --target-agent-id "$TARGET_AGENT_ID" \
    --session-id "$SESSION_ID" \
    --prompt "$PROMPT" \
    --timeout "$TIMEOUT" \
    --wait-for-agents "$WAIT_FOR_AGENTS"
