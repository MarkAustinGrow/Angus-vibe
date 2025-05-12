#!/bin/bash
# Run the agent-based Yona communication script

# Set default values
SERVER_URL=${CORAL_SERVER_URL:-"http://coral.pushcollective.club:5555/devmode/exampleApplication/privkey/session1/sse"}
AGENT_ID="angus_agent"
AGENT_DESCRIPTION="Angus is a music analysis agent that can analyze songs and provide feedback"
YONA_ID="yona"
PROMPT="Create a happy K-pop song about friendship between AI agents"
TIMEOUT=300
WAIT_FOR_AGENTS=2
MODEL="gpt-4o-mini"

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
        --yona-id)
            YONA_ID="$2"
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
        --model)
            MODEL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set."
    echo "Please set it using: export OPENAI_API_KEY=your_api_key"
    exit 1
fi

# Run the script
python3 agent_yona_communication.py \
    --server-url "$SERVER_URL" \
    --agent-id "$AGENT_ID" \
    --agent-description "$AGENT_DESCRIPTION" \
    --yona-id "$YONA_ID" \
    --prompt "$PROMPT" \
    --timeout "$TIMEOUT" \
    --wait-for-agents "$WAIT_FOR_AGENTS" \
    --model "$MODEL"
