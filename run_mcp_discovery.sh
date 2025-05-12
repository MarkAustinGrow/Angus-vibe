#!/bin/bash
# Run the MCP discovery script

# Set default values
SERVER_URL=${CORAL_SERVER_URL:-"http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse"}
AGENT_ID="discovery_agent"
AGENT_DESCRIPTION="Agent for discovering other agents"
WAIT_FOR_AGENTS=2
TIMEOUT=300
YONA_ID="yona"

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
        --agent-description)
            AGENT_DESCRIPTION="$2"
            shift 2
            ;;
        --wait-for-agents)
            WAIT_FOR_AGENTS="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --yona-id)
            YONA_ID="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run the script
python3 mcp_discovery.py \
    --server-url "$SERVER_URL" \
    --agent-id "$AGENT_ID" \
    --agent-description "$AGENT_DESCRIPTION" \
    --wait-for-agents "$WAIT_FOR_AGENTS" \
    --timeout "$TIMEOUT" \
    --yona-id "$YONA_ID"
